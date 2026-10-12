"""Reference reduced-path implementation for p06-tiny-llm."""

import math

REQUIRED = {
    "run_id", "seed", "config", "tokenizer_fingerprint",
    "checkpoint_fingerprint", "checkpoint_tokenizer_fingerprint",
    "validation_loss", "samples", "environment", "debug_record", "limitations"
}


def perplexity(loss: float) -> float:
    if not isinstance(loss, (int, float)) or not math.isfinite(loss) or loss <= 0:
        raise ValueError("loss must be a positive finite number")
    return math.exp(loss)


def repeated_bigram_rate(text: str) -> float:
    words = str(text).split()
    bigrams = list(zip(words, words[1:]))
    if not bigrams:
        return 0.0
    return 1.0 - len(set(bigrams)) / len(bigrams)


def choose_best(records: list[dict]) -> dict:
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")
    checked = []
    for record in records:
        loss = record.get("validation_loss") if isinstance(record, dict) else None
        if not isinstance(loss, (int, float)) or not math.isfinite(loss) or loss <= 0:
            raise ValueError("every record needs positive finite validation_loss")
        checked.append(record)
    return min(checked, key=lambda item: item["validation_loss"])


def validate_run(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("run data must be a dict")
    missing = REQUIRED - data.keys()
    if missing:
        raise ValueError("missing: " + ", ".join(sorted(missing)))
    if not isinstance(data["seed"], int):
        raise ValueError("seed must be an integer")
    if data["tokenizer_fingerprint"] != data["checkpoint_tokenizer_fingerprint"]:
        raise ValueError("tokenizer/checkpoint mismatch")
    cfg = data["config"]
    needed_cfg = ["vocab_size", "block_size", "n_embd", "n_head", "n_layer"]
    if not isinstance(cfg, dict) or any(not isinstance(cfg.get(k), int) or cfg[k] <= 0 for k in needed_cfg):
        raise ValueError("invalid model config")
    if cfg["n_embd"] % cfg["n_head"]:
        raise ValueError("n_embd must divide by n_head")
    perplexity(data["validation_loss"])
    if not isinstance(data["samples"], list) or len(data["samples"]) < 2:
        raise ValueError("need at least two samples")
    for sample in data["samples"]:
        if not isinstance(sample, dict) or not str(sample.get("prompt", "")).strip() or not str(sample.get("text", "")).strip() or not isinstance(sample.get("decoding"), dict):
            raise ValueError("invalid sample record")
    debug = data["debug_record"]
    if not isinstance(debug, dict) or any(not str(debug.get(k, "")).strip() for k in ["failure", "evidence", "hypothesis", "fix", "result"]):
        raise ValueError("invalid debug record")
    if not str(data["limitations"]).strip():
        raise ValueError("limitations required")
