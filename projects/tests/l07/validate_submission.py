#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path

REQUIRED_RUN_FIELDS = {
    "workflow_id", "model_id", "prompt_version", "decoding",
    "source_catalog", "cases", "debug_record", "limitations"
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p07_submission", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def basic_run_contract(data: dict) -> None:
    missing = sorted(REQUIRED_RUN_FIELDS - data.keys())
    if missing:
        fail("workflow run missing: " + ", ".join(missing))
    for key in ["workflow_id", "model_id", "prompt_version"]:
        if not str(data.get(key, "")).strip():
            fail(f"{key} must be non-empty")
    if not isinstance(data["decoding"], dict) or not str(data["decoding"].get("mode", "")).strip():
        fail("decoding must include a mode")
    catalog = data["source_catalog"]
    if not isinstance(catalog, dict) or not catalog:
        fail("source_catalog must be a non-empty object")
    if not isinstance(data["cases"], list) or len(data["cases"]) < 4:
        fail("at least four fixed evaluation cases are required")
    ids = []
    for case in data["cases"]:
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            fail("each case needs an id")
        ids.append(case_id)
        if not str(case.get("query", "")).strip():
            fail("each case needs a query")
        supplied = case.get("supplied_source_ids")
        if not isinstance(supplied, list) or any(source_id not in catalog for source_id in supplied):
            fail(f"{case_id}: supplied sources must exist in source_catalog")
        if type(case.get("expected_supported")) is not bool:
            fail(f"{case_id}: expected_supported must be bool")
        if not isinstance(case.get("output"), dict):
            fail(f"{case_id}: output must be an object")
    if len(ids) != len(set(ids)):
        fail("case ids must be unique")
    debug = data["debug_record"]
    if not isinstance(debug, dict) or not all(str(debug.get(k, "")).strip() for k in ["failure", "evidence", "hypothesis", "fix", "result"]):
        fail("debug_record needs failure/evidence/hypothesis/fix/result")
    if not str(data["limitations"]).strip():
        fail("limitations must be non-empty")


def objective_checks(module, run_data: dict) -> None:
    for name in ["word_overlap", "retrieve", "validate_model_output", "evaluate_cases", "validate_run"]:
        if not callable(getattr(module, name, None)):
            fail(f"missing callable {name}")

    if module.word_overlap("Cedar launch month", "Project Cedar launch month is May") < 3:
        fail("word_overlap should count shared normalized words")

    docs = {
        "schedule": "The meeting is Tuesday.",
        "month": "Project Cedar launch month is May.",
        "team": "Mina is on Project Cedar.",
    }
    if module.retrieve("What is the Cedar launch month?", docs, 1) != ["month"]:
        fail("retrieve should rank the most overlapping document first")
    if len(module.retrieve("Cedar", docs, 2)) != 2:
        fail("retrieve must respect k")

    module.validate_model_output(
        {"answer": "10 hours", "supported": True, "source_id": "battery"},
        ["battery"],
    )
    module.validate_model_output(
        {"answer": None, "supported": False, "source_id": None},
        ["battery"],
    )
    try:
        module.validate_model_output(
            {"answer": "1.8 kg", "supported": True, "source_id": "weight"},
            ["battery"],
        )
    except ValueError:
        pass
    else:
        fail("validate_model_output must reject an unsupplied source")

    passed, failed = module.evaluate_cases(run_data["cases"])
    if passed != len(run_data["cases"]) or failed:
        fail("reference-compatible run cases should all pass")

    module.validate_run(run_data)

    missing = dict(run_data)
    missing.pop("prompt_version", None)
    try:
        module.validate_run(missing)
    except ValueError:
        pass
    else:
        fail("validate_run must reject a missing required field")

    tampered = json.loads(json.dumps(run_data))
    tampered["cases"][0]["output"]["source_id"] = next(
        source_id
        for source_id in tampered["source_catalog"]
        if source_id not in tampered["cases"][0]["supplied_source_ids"]
    )
    try:
        module.validate_run(tampered)
    except ValueError:
        pass
    else:
        fail("validate_run must reject output provenance outside supplied context")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_submission.py SUBMISSION.py WORKFLOW-RUN.json")
    module_path = Path(sys.argv[1])
    run_path = Path(sys.argv[2])
    if not module_path.is_file() or not run_path.is_file():
        raise SystemExit("submission module and workflow-run.json must exist")
    data = json.loads(run_path.read_text(encoding="utf-8"))
    basic_run_contract(data)
    objective_checks(load_module(module_path), data)
    print("PASS: p07-reliable-llm-workflow objective checks")


if __name__ == "__main__":
    main()
