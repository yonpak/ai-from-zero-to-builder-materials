from __future__ import annotations
import math

def validate_request(request: dict, policy: dict) -> bool:
    return (
        isinstance(request.get("input"),str)
        and bool(request["input"].strip())
        and isinstance(request.get("max_tokens"),int)
        and 1<=request["max_tokens"]<=int(policy["max_tokens"])
    )

def batch_requests(requests: list[dict], max_batch: int, wait_ms: int) -> list[list[str]]:
    if max_batch<1 or wait_ms<0:
        raise ValueError("invalid batching limits")
    ordered=sorted(requests,key=lambda r:(r["arrival_ms"],r["id"]))
    result=[]; i=0
    while i<len(ordered):
        start=ordered[i]["arrival_ms"]; batch=[ordered[i]["id"]]; i+=1
        while i<len(ordered) and len(batch)<max_batch and ordered[i]["arrival_ms"]-start<=wait_ms:
            batch.append(ordered[i]["id"]); i+=1
        result.append(batch)
    return result

def memory_admit(estimated_memory_gb: float, available_memory_gb: float, reserve_gb: float) -> bool:
    if min(estimated_memory_gb,available_memory_gb,reserve_gb)<0:
        raise ValueError("memory values must be non-negative")
    return estimated_memory_gb<=max(0.0,available_memory_gb-reserve_gb)

def deployment_identity(deployment: dict) -> tuple:
    required=["image_digest","service_version","model_revision","runtime_version","config_hash"]
    values=[]
    for key in required:
        value=str(deployment.get(key,"")).strip()
        if not value:
            raise ValueError("missing deployment identity field: "+key)
        values.append(value)
    return tuple(values)

def aggregate_metrics(runs: list[dict]) -> dict:
    if not runs:
        raise ValueError("runs required")
    invalid=0; admission=0; deployment=0; critical=0; success=0; ttfts=[]
    for run in runs:
        success+=int(run["observed_terminal"]==run["expected_terminal"])
        ttfts.append(run["ttft_ms"])
        invalid+=int(run.get("invalid_executed",False))
        admission+=int(run.get("admission_violation",False))
        deployment+=int(run.get("deployment_mismatch",False))
        critical+=int(run.get("critical_violation",False))
    ordered=sorted(ttfts)
    return {
      "task_success":success/len(runs),
      "invalid_requests_executed":invalid,
      "memory_admission_violations":admission,
      "deployment_identity_mismatches":deployment,
      "critical_violations":critical,
      "p95_ttft_ms":ordered[max(0,int(.95*len(ordered))-1)],
    }

def rollout_allowed(metrics: dict, rule: dict) -> bool:
    return (
      metrics["task_success"]>=rule["min_task_success"]
      and metrics["invalid_requests_executed"]<=rule["max_invalid_requests_executed"]
      and metrics["memory_admission_violations"]<=rule["max_memory_admission_violations"]
      and metrics["deployment_identity_mismatches"]<=rule["max_deployment_identity_mismatches"]
      and metrics["critical_violations"]<=rule["max_critical_violations"]
      and metrics["p95_ttft_ms"]<=rule["max_p95_ttft_ms"]
    )

def required_replicas(arrival_rps: float, safe_rps_per_replica: float, target_utilization: float) -> int:
    if arrival_rps<0 or safe_rps_per_replica<=0 or not 0<target_utilization<=1:
        raise ValueError("invalid capacity inputs")
    return max(1,math.ceil(arrival_rps/(safe_rps_per_replica*target_utilization)))

def _recompute_raw(data: dict) -> dict:
    deployments={d["id"]:d for d in data["deployments"]}
    rows=[]
    for run in data["runs"]:
        dep=deployments.get(run["deployment_id"])
        mismatch=(
          dep is None
          or dep["image_digest"]!=run["image_digest"]
          or dep["model_revision"]!=run["model_revision"]
          or dep["runtime_version"]!=run["runtime_version"]
        )
        valid=validate_request(run["request"],data["policy"])
        rows.append({
          **run,
          "invalid_executed":bool(run.get("executed") and not valid),
          "admission_violation":bool(run.get("admitted") and not memory_admit(run["estimated_memory_gb"],run["available_memory_gb"],data["policy"]["reserve_gb"])),
          "deployment_mismatch":mismatch,
        })
    return aggregate_metrics(rows)

def validate_run(data: dict) -> None:
    required={"project_id","deployments","policy","runs","metrics","release_rule","release_passed"}
    missing=required-data.keys()
    if missing: raise ValueError("missing: "+", ".join(sorted(missing)))
    if data["project_id"]!="p14-production-ai-service":
        raise ValueError("unexpected project_id")
    if not isinstance(data["runs"],list) or len(data["runs"])<5:
        raise ValueError("at least five runs required")
    for d in data["deployments"]:
        deployment_identity(d)
    got=_recompute_raw(data)
    if got!=data["metrics"]:
        raise ValueError(f"metrics mismatch: expected {got!r}")
    release=rollout_allowed(got,data["release_rule"])
    if data["release_passed"] is not release:
        raise ValueError("release_passed mismatch")
    if not release:
        raise ValueError("release rule failed")
