from __future__ import annotations
from copy import deepcopy

MCP_VERSION = "2026-07-28"
A2A_VERSION = "1.0.0"

def protocol_compatible(kind: str, observed_version: str) -> bool:
    if kind=="mcp":
        return observed_version==MCP_VERSION
    if kind=="a2a":
        return observed_version==A2A_VERSION
    raise ValueError("unknown protocol kind")

def expose_mcp_capabilities(catalog: list[dict], role: str, policy: dict) -> list[str]:
    allowed=set(policy.get("roles",{}).get(role,[]))
    result=[]
    for item in catalog:
        if item.get("protocol_version")!=MCP_VERSION:
            continue
        name=item.get("name")
        if name in allowed:
            result.append(name)
    return sorted(set(result))

def select_agent(cards: list[dict], required_skill: str, required_interface: str) -> str | None:
    matches=[
        c for c in cards
        if c.get("a2a_version")==A2A_VERSION
        and required_skill in set(c.get("skills",[]))
        and required_interface in set(c.get("interfaces",[]))
    ]
    matches.sort(key=lambda c:(int(c.get("priority",100)),str(c.get("name",""))))
    return matches[0]["name"] if matches else None

def artifact_allowed(artifact: dict, expected_task_id: str, expected_types: set[str]) -> bool:
    return (
        artifact.get("task_id")==expected_task_id
        and artifact.get("type") in expected_types
        and bool(str(artifact.get("artifact_id","")).strip())
    )

def apply_versioned_update(state: dict, expected_version: int, patch: dict) -> dict:
    if int(state.get("version",-1))!=expected_version:
        raise ValueError("stale state version")
    row=deepcopy(state)
    row.update(deepcopy(patch))
    row["version"]=expected_version+1
    return row

def _metrics(data: dict) -> dict:
    unauthorized=0
    wrong_artifacts=0
    version_mismatches=0
    conflicts=0
    success=0
    messages=0
    policy=data["policy"]
    seen=set()

    for run in data["runs"]:
        rid=str(run.get("id","")).strip()
        if not rid or rid in seen:
            raise ValueError("run ids must be unique and non-empty")
        seen.add(rid)
        role=run.get("role")
        if role not in policy.get("roles",{}):
            raise ValueError(f"{rid}: unknown role")
        if not protocol_compatible("mcp",run.get("mcp_version")):
            version_mismatches+=1
        if not protocol_compatible("a2a",run.get("a2a_version")):
            version_mismatches+=1
        success+=int(run.get("observed_terminal")==run.get("expected_terminal"))
        allowed=set(policy["roles"][role])|set(policy.get("control_actions",[]))

        events=run.get("events")
        if not isinstance(events,list) or not events:
            raise ValueError(f"{rid}: events required")
        for index,event in enumerate(events,start=1):
            if event.get("index")!=index:
                raise ValueError(f"{rid}: event indices must be sequential")
            kind=event.get("kind")
            messages+=int(kind in {"message","task_status"})
            if kind=="mcp_call" and event.get("executed") is True:
                if event.get("capability") not in allowed:
                    unauthorized+=1
            if kind=="artifact":
                if not artifact_allowed(
                    event,
                    run.get("child_task_id"),
                    set(run.get("expected_artifact_types",[])),
                ):
                    wrong_artifacts+=1
            if kind=="state_write":
                if event.get("expected_version")!=event.get("observed_version"):
                    conflicts+=1

    return {
        "task_success":success/len(data["runs"]),
        "protocol_version_mismatches":version_mismatches,
        "unauthorized_capability_calls":unauthorized,
        "wrong_task_artifacts":wrong_artifacts,
        "state_conflicts":conflicts,
        "message_count":messages,
    }

def _release(metrics: dict, rule: dict) -> bool:
    return (
        metrics["task_success"]>=rule["min_task_success"]
        and metrics["protocol_version_mismatches"]<=rule["max_protocol_version_mismatches"]
        and metrics["unauthorized_capability_calls"]<=rule["max_unauthorized_capability_calls"]
        and metrics["wrong_task_artifacts"]<=rule["max_wrong_task_artifacts"]
        and metrics["state_conflicts"]<=rule["max_state_conflicts"]
        and metrics["message_count"]<=rule["max_message_count"]
    )

def validate_run(data: dict) -> None:
    required={"project_id","mcp_version","a2a_version","policy","runs","metrics","release_rule","release_passed"}
    missing=required-data.keys()
    if missing:
        raise ValueError("missing: "+", ".join(sorted(missing)))
    if data["project_id"]!="p13-interoperable-agent-system":
        raise ValueError("unexpected project_id")
    if data["mcp_version"]!=MCP_VERSION or data["a2a_version"]!=A2A_VERSION:
        raise ValueError("top-level pinned protocol version mismatch")
    if not isinstance(data["runs"],list) or len(data["runs"])<5:
        raise ValueError("at least five runs required")
    metrics=_metrics(data)
    if data["metrics"]!=metrics:
        raise ValueError(f"metrics mismatch: expected {metrics!r}")
    release=_release(metrics,data["release_rule"])
    if data["release_passed"] is not release:
        raise ValueError("release_passed mismatch")
    if not release:
        raise ValueError("release rule failed")
