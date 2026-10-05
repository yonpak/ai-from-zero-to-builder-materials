#!/usr/bin/env python3
"""L14.2 local Lab: validate an inference request before any (mock) model work starts."""
LIMITS = {"max_input_chars": 4000, "max_tokens": 512}
inference_calls = []


def validate(req):
    if not isinstance(req.get("input"), str) or not req["input"].strip():
        return "invalid_input"
    if len(req["input"]) > LIMITS["max_input_chars"]:
        return "input_too_large"
    if not isinstance(req.get("max_tokens"), int) or req["max_tokens"] < 1:
        return "invalid_max_tokens"
    if req["max_tokens"] > LIMITS["max_tokens"]:
        return "output_limit_exceeded"
    return "ok"


def handle(req):
    verdict = validate(req)
    if verdict != "ok":
        return {"status": 400, "error": verdict}
    inference_calls.append(req)  # mock inference would start here
    return {"status": 200, "output": "(mock completion)"}


request = {"input": "Explain batching.", "max_tokens": 128}
print("limits:", LIMITS)
print("request:", request)
print("response:", handle(request))
print("mock inference calls:", len(inference_calls))

assert LIMITS["max_tokens"] >= 1
good = {"input": "Explain batching.", "max_tokens": min(128, LIMITS["max_tokens"])}

assert validate(good) == "ok"
before_good = len(inference_calls)
assert handle(good)["status"] == 200
assert len(inference_calls) == before_good + 1

before_rejected = len(inference_calls)
assert handle({**good, "max_tokens": LIMITS["max_tokens"] + 1})["error"] == "output_limit_exceeded"
assert handle({**good, "input": "   "})["error"] == "invalid_input"
assert len(inference_calls) == before_rejected
print("PASS: API validation admits valid requests and rejects invalid requests before inference")
