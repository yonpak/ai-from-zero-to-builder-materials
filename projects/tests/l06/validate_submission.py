#!/usr/bin/env python3
import importlib.util
import json
import math
import sys
from pathlib import Path

REQUIRED_RUN_FIELDS = {
    "run_id", "seed", "config", "tokenizer_fingerprint",
    "checkpoint_fingerprint", "checkpoint_tokenizer_fingerprint",
    "validation_loss", "samples", "environment", "debug_record", "limitations"
}
REQUIRED_CONFIG_FIELDS = {"vocab_size", "block_size", "n_embd", "n_head", "n_layer"}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("p06_submission", path)
    if spec is None or spec.loader is None:
        fail(f"cannot import submission: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def objective_checks(module, run_data: dict) -> None:
    for name in ["perplexity", "repeated_bigram_rate", "choose_best", "validate_run"]:
        if not callable(getattr(module, name, None)):
            fail(f"missing callable {name}")

    p = module.perplexity(2.0)
    if not math.isclose(p, math.exp(2.0), rel_tol=1e-9):
        fail("perplexity must equal exp(loss)")
    for bad in [0.0, -1.0, math.inf, math.nan]:
        try:
            module.perplexity(bad)
        except (ValueError, TypeError):
            pass
        else:
            fail("perplexity must reject non-positive/non-finite loss")

    loop = module.repeated_bigram_rate("the cat the cat the cat the cat")
    varied = module.repeated_bigram_rate("the cat sat near a warm window")
    if not (0 <= varied < loop <= 1):
        fail("repeated_bigram_rate should score the intentional loop higher")

    records = [
        {"step": 20, "validation_loss": 3.1},
        {"step": 40, "validation_loss": 2.7},
        {"step": 60, "validation_loss": 2.9},
    ]
    if module.choose_best(records).get("step") != 40:
        fail("choose_best must select the lowest validation_loss")

    module.validate_run(run_data)

    missing = dict(run_data)
    missing.pop("seed", None)
    try:
        module.validate_run(missing)
    except ValueError:
        pass
    else:
        fail("validate_run must reject a missing required field")

    mismatch = dict(run_data)
    mismatch["checkpoint_tokenizer_fingerprint"] = "wrong-tokenizer"
    try:
        module.validate_run(mismatch)
    except ValueError:
        pass
    else:
        fail("validate_run must reject tokenizer/checkpoint mismatch")


def basic_run_contract(data: dict) -> None:
    missing = sorted(REQUIRED_RUN_FIELDS - data.keys())
    if missing:
        fail("run.json missing: " + ", ".join(missing))
    if not isinstance(data["seed"], int):
        fail("seed must be an integer")
    if not isinstance(data["config"], dict) or REQUIRED_CONFIG_FIELDS - data["config"].keys():
        fail("config must include vocab_size, block_size, n_embd, n_head, n_layer")
    cfg = data["config"]
    if not all(isinstance(cfg[k], int) and cfg[k] > 0 for k in REQUIRED_CONFIG_FIELDS):
        fail("all required config dimensions must be positive integers")
    if cfg["n_embd"] % cfg["n_head"] != 0:
        fail("n_embd must divide evenly by n_head")
    if data["tokenizer_fingerprint"] != data["checkpoint_tokenizer_fingerprint"]:
        fail("checkpoint/tokenizer fingerprint mismatch")
    if not isinstance(data["validation_loss"], (int, float)) or not math.isfinite(data["validation_loss"]) or data["validation_loss"] <= 0:
        fail("validation_loss must be a positive finite number")
    if not isinstance(data["samples"], list) or len(data["samples"]) < 2:
        fail("samples must contain at least two fixed evaluation samples")
    for sample in data["samples"]:
        if not isinstance(sample, dict) or not all(str(sample.get(k, "")).strip() for k in ["prompt", "text"]):
            fail("each sample needs prompt and text")
        if not isinstance(sample.get("decoding"), dict):
            fail("each sample needs a decoding settings object")
    debug = data["debug_record"]
    if not isinstance(debug, dict) or not all(str(debug.get(k, "")).strip() for k in ["failure", "evidence", "hypothesis", "fix", "result"]):
        fail("debug_record needs failure/evidence/hypothesis/fix/result")
    if not str(data["limitations"]).strip():
        fail("limitations must be non-empty")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_submission.py SUBMISSION.py RUN.json")
    module_path = Path(sys.argv[1])
    run_path = Path(sys.argv[2])
    if not module_path.is_file() or not run_path.is_file():
        raise SystemExit("submission module and run.json must exist")
    data = json.loads(run_path.read_text(encoding="utf-8"))
    basic_run_contract(data)
    objective_checks(load_module(module_path), data)
    print("PASS: p06-tiny-llm objective checks")

if __name__ == "__main__":
    main()
