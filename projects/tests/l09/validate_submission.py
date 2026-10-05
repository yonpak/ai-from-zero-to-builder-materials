#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p09_submission", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def objective_checks(module, run_data: dict) -> None:
    for name in [
        "token_overlap",
        "eligible_source_ids",
        "retrieve",
        "validate_grounded_output",
        "validate_run",
    ]:
        if not callable(getattr(module, name, None)):
            fail(f"missing callable {name}")

    if module.token_overlap("cedar return policy", "Current Cedar return policy allows 30 days") < 3:
        fail("token_overlap should count normalized shared words")

    catalog = {
        "cedar-current": {"text": "Cedar return policy 30 days", "tenant_id": "cedar", "active": True},
        "cedar-old": {"text": "Cedar return policy 14 days", "tenant_id": "cedar", "active": False},
        "maple": {"text": "Maple return policy 60 days", "tenant_id": "maple", "active": True},
    }
    if module.eligible_source_ids(catalog, "cedar") != ["cedar-current"]:
        fail("eligibility must filter tenant and active state before ranking")
    if module.retrieve("cedar return policy", catalog, "cedar", 2) != ["cedar-current"]:
        fail("retrieve must rank only eligible sources")

    module.validate_grounded_output(
        {"answer": "30 days", "supported": True, "source_id": "cedar-current"},
        ["cedar-current"],
    )
    module.validate_grounded_output(
        {"answer": None, "supported": False, "source_id": None},
        ["cedar-current"],
    )
    try:
        module.validate_grounded_output(
            {"answer": "60 days", "supported": True, "source_id": "maple"},
            ["cedar-current"],
        )
    except ValueError:
        pass
    else:
        fail("grounded output must reject an unsupplied source")

    module.validate_run(run_data)

    tampered = json.loads(json.dumps(run_data))
    tampered["cases"][0]["supplied_source_ids"] = ["maple-private"]
    tampered["cases"][0]["retrieved_ids"] = ["maple-private", "cedar-battery-v2"]
    tampered["cases"][0]["output"] = {
        "answer": "gold",
        "supported": True,
        "source_id": "maple-private",
    }
    tampered["metrics"]["unauthorized_exposure_count"] = 2
    tampered["metrics"]["grounded_accuracy"] = 0.75
    tampered["release_passed"] = False
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must reject cross-tenant evidence exposure")

    tampered = json.loads(json.dumps(run_data))
    tampered["cases"][0]["output"]["source_id"] = "cedar-weight-v2"
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must reject a citation outside supplied evidence")

    tampered = json.loads(json.dumps(run_data))
    tampered["release_passed"] = not tampered["release_passed"]
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must recompute the release decision")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_submission.py SUBMISSION.py RAG-RUN.json")
    module_path = Path(sys.argv[1])
    run_path = Path(sys.argv[2])
    if not module_path.is_file() or not run_path.is_file():
        raise SystemExit("submission module and rag-run.json must exist")
    data = json.loads(run_path.read_text(encoding="utf-8"))
    objective_checks(load_module(module_path), data)
    print("PASS: p09-evidence-rag objective checks")


if __name__ == "__main__":
    main()
