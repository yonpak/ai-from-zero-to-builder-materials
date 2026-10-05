# Production AI Service

Build the operational controller around a production inference service.

## Implement

Complete the TODO functions in `service.py`:

1. bounded inference request validation;
2. deadline/size-bounded batching;
3. memory admission with reserve headroom;
4. immutable deployment identity;
5. serving metric aggregation;
6. rollout release gates;
7. replica capacity planning;
8. raw-evidence run validation.

The required acceptance path is deterministic and does not require a GPU, live model server, Kubernetes cluster, cloud account, network call, or secret.

Run:

    python3 projects/tests/l14/validate_submission.py \
      projects/starters/l14/service.py \
      projects/tests/l14/fixtures/passing/service-run.json

Reference acceptance:

    python3 projects/tests/l14/test_reference.py

Level Labs:

    python3 labs/notebooks/level-14/test_labs.py

## Optional real-model serving extension

After the deterministic controller passes, install the optional real-model environment and run the Level 14 serving exercise:

    pip install -r labs/real-model/requirements.txt
    python labs/real-model/l14_real_model_serving.py --requests 6 --concurrency 2

This starts a fallback local HTTP service around a real instruction-tuned model, demonstrates liveness versus readiness, sends concurrent requests, and reports client-observed time to first streamed text, p95 end-to-end latency, and throughput. The fallback deliberately serializes generation so queueing is visible. Runtime-level generation failures, missing stream completion, or a prolonged stream stall mark the fallback not ready rather than leaving readiness green after inference has failed. Add `--demo-readiness-failure` to inject one controlled worker failure after the normal benchmark and verify the next readiness request returns 503.

To exercise a real serving scheduler, start vLLM separately and point the same benchmark at its OpenAI-compatible endpoint. The measurement process is a standard-library HTTP client in this mode, so it can run in a plain Python 3.10+ environment without `torch`, `transformers`, or the full real-model requirements. Keep those heavy dependencies in the vLLM server environment.

    # server environment
    vllm serve Qwen/Qwen2.5-0.5B-Instruct

    # separate measurement environment
    python labs/real-model/l14_real_model_serving.py \
      --openai-base-url http://127.0.0.1:8000 \
      --model Qwen/Qwen2.5-0.5B-Instruct \
      --requests 12 --concurrency 4

The client metric is named `first_stream_ms`, not TTFT, because a decoded text chunk may contain more than one raw token. Use server-native metrics when exact token-level TTFT is required.

Use the deterministic project to prove controller logic. Use the fallback to see queueing boundaries around a real model, then use the vLLM path to observe a serving runtime that can schedule concurrent requests.

## Docker bridge

The included Dockerfile gives you a reproducible Python container for serving-control experiments. Real GPU serving additionally depends on compatible device/runtime infrastructure that is intentionally outside the required local acceptance path.
