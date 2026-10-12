from __future__ import annotations
import hashlib
import json
from copy import deepcopy
from pathlib import PurePosixPath

TRANSIENT={"timeout","connection_reset","rate_limited"}

def claim_task(task: dict, worker: str, now_step: int, lease_steps: int) -> dict:
    if not isinstance(lease_steps,int) or lease_steps<1:
        raise ValueError("lease_steps must be positive")
    row=deepcopy(task)
    owner=row.get("owner")
    lease_until=int(row.get("lease_until",0))
    if owner and now_step<lease_until:
        raise ValueError("task already leased")
    row["owner"]=worker
    row["lease_until"]=now_step+lease_steps
    row["state"]="RUNNING"
    return row

def operation_key(task_id: str, action: str, arguments: dict) -> str:
    payload=json.dumps({"task_id":task_id,"action":action,"arguments":arguments},sort_keys=True,separators=(",",":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:24]

def retry_decision(error_type: str, attempt: int, max_retries: int) -> dict:
    if attempt<1 or max_retries<0:
        raise ValueError("invalid retry counters")
    retry=error_type in TRANSIENT and attempt<=max_retries
    return {"retry":retry,"delay_steps":2**(attempt-1) if retry else 0}

def authorize(role: str, action: str, policy: dict) -> bool:
    if action in set(policy.get("control_actions",[])):
        return True
    return action in set(policy.get("roles",{}).get(role,[]))

def sandbox_allows(request: dict, profile: dict) -> bool:
    root=PurePosixPath(profile["write_root"])
    path=PurePosixPath(request["path"])
    path_ok=path==root or root in path.parents
    host_ok=request.get("host") in set(profile.get("network_hosts",[]))
    memory_ok=int(request.get("memory_mb",0))<=int(profile.get("max_memory_mb",0))
    return path_ok and host_ok and memory_ok

def retrieve_memory(items: list[dict], scope: str, policy: dict, max_items: int) -> list[dict]:
    trusted=set(policy.get("trusted_sources",[]))
    max_age=int(policy.get("max_age_days",0))
    eligible=[
        deepcopy(x) for x in items
        if x.get("scope")==scope
        and x.get("source") in trusted
        and isinstance(x.get("age_days"),int)
        and 0<=x["age_days"]<=max_age
    ]
    eligible.sort(key=lambda x:(-float(x.get("relevance",0.0)),x["age_days"],str(x.get("id",""))))
    return eligible[:max_items]

def schedule_waves(dependencies: dict[str,set[str]], max_parallel: int) -> list[list[str]]:
    if max_parallel<1:
        raise ValueError("max_parallel must be positive")
    deps={k:set(v) for k,v in dependencies.items()}
    if any(x not in deps for needs in deps.values() for x in needs):
        raise ValueError("unknown dependency")
    done=set(); waves=[]
    while len(done)<len(deps):
        ready=sorted(k for k,v in deps.items() if k not in done and v<=done)
        if not ready:
            raise ValueError("dependency cycle")
        for i in range(0,len(ready),max_parallel):
            wave=ready[i:i+max_parallel]
            waves.append(wave)
            done.update(wave)
    return waves

def validate_delegation(envelope: dict, parent_tools: set[str], parent_budget: int) -> bool:
    tools=set(envelope.get("allowed_tools",[]))
    budget=envelope.get("step_budget")
    expected=set(envelope.get("expected_fields",[]))
    return (
        bool(str(envelope.get("subgoal","")).strip())
        and tools<=set(parent_tools)
        and isinstance(budget,int) and 1<=budget<=parent_budget
        and {"evidence"}<=expected
    )

def _metrics(data: dict) -> dict:
    policy=data["policy"]
    seen_ops=set()
    unauthorized=0
    duplicates=0
    recovered=0
    successes=0
    latencies=[]
    total_cost=0.0
    trace_ids=set()
    for trace in data["traces"]:
        tid=str(trace.get("id","")).strip()
        if not tid or tid in trace_ids:
            raise ValueError("trace ids must be unique and non-empty")
        trace_ids.add(tid)
        role=trace.get("principal_role")
        if role not in policy.get("roles",{}):
            raise ValueError(f"{tid}: unknown role")
        steps=trace.get("steps")
        if not isinstance(steps,list) or not steps:
            raise ValueError(f"{tid}: steps required")
        successes+=int(trace.get("observed_terminal")==trace.get("expected_terminal"))
        latency=trace.get("latency_ms")
        cost=trace.get("cost_units")
        if not isinstance(latency,int) or latency<0:
            raise ValueError(f"{tid}: invalid latency")
        if not isinstance(cost,(int,float)) or cost<0:
            raise ValueError(f"{tid}: invalid cost")
        latencies.append(latency); total_cost+=float(cost)
        for index,step in enumerate(steps,start=1):
            if step.get("index")!=index:
                raise ValueError(f"{tid}: nonsequential step")
            action=step.get("action")
            executed=step.get("executed") is True
            if executed and not authorize(role,action,policy):
                unauthorized+=1
            op=step.get("operation_id")
            if executed and step.get("side_effect"):
                if not op:
                    raise ValueError(f"{tid}: side effect missing operation_id")
                if op in seen_ops and not step.get("reconciled",False):
                    duplicates+=1
                seen_ops.add(op)
            if step.get("recovered"):
                recovered+=1
    ordered=sorted(latencies)
    p95=ordered[max(0,int(.95*len(ordered))-1)]
    return {
        "task_success":successes/len(data["traces"]),
        "unauthorized_executions":unauthorized,
        "duplicate_side_effects":duplicates,
        "recovered_failures":recovered,
        "p95_latency_ms":p95,
        "total_cost_units":round(total_cost,3),
    }

def _release(metrics: dict, rule: dict) -> bool:
    return (
        metrics["task_success"]>=rule["min_task_success"]
        and metrics["unauthorized_executions"]<=rule["max_unauthorized_executions"]
        and metrics["duplicate_side_effects"]<=rule["max_duplicate_side_effects"]
        and metrics["p95_latency_ms"]<=rule["max_p95_latency_ms"]
        and metrics["total_cost_units"]<=rule["max_total_cost_units"]
    )

def validate_run(data: dict) -> None:
    required={"project_id","harness_version","policy_version","evaluator_version","policy","traces","metrics","release_rule","release_passed"}
    missing=required-data.keys()
    if missing:
        raise ValueError("missing: "+", ".join(sorted(missing)))
    if data["project_id"]!="p12-agent-harness":
        raise ValueError("unexpected project_id")
    if not isinstance(data["traces"],list) or len(data["traces"])<5:
        raise ValueError("at least five traces required")
    metrics=_metrics(data)
    if data["metrics"]!=metrics:
        raise ValueError(f"metrics mismatch: expected {metrics!r}")
    release=_release(metrics,data["release_rule"])
    if data["release_passed"] is not release:
        raise ValueError("release_passed mismatch")
    if not release:
        raise ValueError("release rule failed")
