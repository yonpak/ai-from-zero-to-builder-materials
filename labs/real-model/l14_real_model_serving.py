#!/usr/bin/env python3
"""Optional Level 14 extension: measure a local model server or an OpenAI-compatible serving runtime."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import queue
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
STREAM_POLL_S = 1
STREAM_STALL_TIMEOUT_S = 120


def choose_device(torch_module) -> str:
    if torch_module.cuda.is_available():
        return "cuda"
    if (
        getattr(torch_module.backends, "mps", None)
        and torch_module.backends.mps.is_available()
    ):
        return "mps"
    return "cpu"


def p95(values: list[float]) -> float:
    if not values:
        raise ValueError("at least one latency measurement is required")
    ordered = sorted(values)
    rank = max(1, math.ceil(0.95 * len(ordered)))
    return ordered[rank - 1]


class ModelRuntime:
    def __init__(self, model_id: str) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
        except ImportError as error:
            raise RuntimeError(
                "fallback model serving requires torch and transformers; install "
                "labs/real-model/requirements.txt, or use --openai-base-url to benchmark "
                "an already-running OpenAI-compatible server without those packages"
            ) from error

        self.model_id = model_id
        self._torch = torch
        self._auto_model_cls = AutoModelForCausalLM
        self._auto_tokenizer_cls = AutoTokenizer
        self._text_iterator_streamer_cls = TextIteratorStreamer
        self.device = choose_device(torch)
        self.tokenizer = None
        self.model = None
        self.ready = False
        self.fail_next_generation = False
        self._generation_lock = threading.Lock()

    def load(self) -> None:
        dtype = (
            self._torch.float16
            if self.device in {"cuda", "mps"}
            else self._torch.float32
        )
        self.tokenizer = self._auto_tokenizer_cls.from_pretrained(self.model_id)
        self.model = self._auto_model_cls.from_pretrained(self.model_id, dtype=dtype)
        self.model.to(self.device)
        self.model.eval()
        self.ready = True

    def stream(self, prompt: str, max_new_tokens: int):
        if not self.ready or self.tokenizer is None or self.model is None:
            raise RuntimeError("model is not ready")
        messages = [
            {"role": "system", "content": "Answer briefly and directly."},
            {"role": "user", "content": prompt},
        ]
        batch = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        batch = {key: value.to(self.device) for key, value in batch.items()}
        streamer = self._text_iterator_streamer_cls(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
            timeout=STREAM_POLL_S,
        )
        kwargs = {
            **batch,
            "streamer": streamer,
            "do_sample": False,
            "max_new_tokens": max_new_tokens,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        # The tiny fallback runtime deliberately serializes generation so learners can
        # observe queueing under concurrent HTTP requests. Use --openai-base-url with
        # a real serving runtime such as vLLM to study scheduler/batching behavior.
        with self._generation_lock:
            worker_errors: list[Exception] = []

            def generate_worker() -> None:
                try:
                    if self.fail_next_generation:
                        self.fail_next_generation = False
                        raise RuntimeError("injected readiness-demo generation failure")
                    self.model.generate(**kwargs)
                except Exception as error:  # propagate failures out of the worker thread
                    worker_errors.append(error)

            worker = threading.Thread(target=generate_worker, daemon=True)
            worker.start()
            last_stream_activity = time.monotonic()
            try:
                while True:
                    try:
                        chunk = next(streamer)
                    except StopIteration:
                        break
                    except queue.Empty as error:
                        if worker_errors:
                            self.ready = False
                            raise RuntimeError(
                                "model generation failed before the stream completed; "
                                "fallback runtime marked not ready"
                            ) from worker_errors[0]
                        if not worker.is_alive():
                            self.ready = False
                            raise RuntimeError(
                                "generation ended without a streamer completion signal; "
                                "fallback runtime marked not ready"
                            ) from error
                        if time.monotonic() - last_stream_activity >= STREAM_STALL_TIMEOUT_S:
                            self.ready = False
                            raise TimeoutError(
                                f"no streamed text arrived for {STREAM_STALL_TIMEOUT_S} seconds; "
                                "fallback runtime marked not ready"
                            ) from error
                        continue
                    last_stream_activity = time.monotonic()
                    if chunk:
                        yield chunk
            finally:
                worker.join(timeout=5)

            if worker.is_alive():
                self.ready = False
                raise RuntimeError(
                    "generation thread did not terminate; fallback runtime marked not ready"
                )
            if worker_errors:
                self.ready = False
                raise RuntimeError(
                    "model generation failed; fallback runtime marked not ready"
                ) from worker_errors[0]


def handler_for(runtime: ModelRuntime):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health/live":
                self._json(200, {"live": True})
                return
            if self.path == "/health/ready":
                status = 200 if runtime.ready else 503
                self._json(status, {"ready": runtime.ready, "model_id": runtime.model_id})
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/generate":
                self._json(404, {"error": "not found"})
                return
            if not runtime.ready:
                self._json(503, {"error": "model not ready"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                request = json.loads(self.rfile.read(length) or b"{}")
                prompt = str(request["prompt"]).strip()
                max_new_tokens = int(request.get("max_new_tokens", 48))
                if not prompt or max_new_tokens < 1 or max_new_tokens > 256:
                    raise ValueError("invalid prompt or max_new_tokens")
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                self._json(400, {"error": str(error)})
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.end_headers()
            chunks: list[str] = []
            try:
                for chunk in runtime.stream(prompt, max_new_tokens):
                    chunks.append(chunk)
                    event = json.dumps({"type": "text", "text": chunk}) + "\n"
                    self.wfile.write(event.encode("utf-8"))
                    self.wfile.flush()
                done = json.dumps({"type": "done", "text": "".join(chunks).strip()}) + "\n"
                self.wfile.write(done.encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as error:
                event = json.dumps({"type": "error", "error": str(error)}) + "\n"
                try:
                    self.wfile.write(event.encode("utf-8"))
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return

    return Handler


def fetch_json(url: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def local_request(base_url: str, prompt: str, max_new_tokens: int) -> dict:
    body = json.dumps({"prompt": prompt, "max_new_tokens": max_new_tokens}).encode("utf-8")
    request = urllib.request.Request(
        base_url + "/generate",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    first_stream_at = None
    final_text = ""
    with urllib.request.urlopen(request, timeout=600) as response:
        for raw_line in response:
            event = json.loads(raw_line)
            if event.get("type") == "text" and first_stream_at is None:
                first_stream_at = time.perf_counter()
            if event.get("type") == "error":
                raise RuntimeError(str(event.get("error", "fallback generation failed")))
            if event.get("type") == "done":
                final_text = str(event.get("text", ""))
    finished = time.perf_counter()
    if first_stream_at is None:
        first_stream_at = finished
    return {
        "first_stream_ms": (first_stream_at - started) * 1000,
        "total_ms": (finished - started) * 1000,
        "answer": final_text,
    }


def openai_chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def openai_request(
    base_url: str,
    model: str,
    prompt: str,
    max_new_tokens: int,
    api_key: str | None,
) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "temperature": 0,
        "max_tokens": max_new_tokens,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        openai_chat_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    started = time.perf_counter()
    first_stream_at = None
    text_parts: list[str] = []
    with urllib.request.urlopen(request, timeout=600) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            event = json.loads(data)
            choices = event.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            content = delta.get("content")
            if content:
                if first_stream_at is None:
                    first_stream_at = time.perf_counter()
                text_parts.append(str(content))
    finished = time.perf_counter()
    if first_stream_at is None:
        first_stream_at = finished
    return {
        "first_stream_ms": (first_stream_at - started) * 1000,
        "total_ms": (finished - started) * 1000,
        "answer": "".join(text_parts).strip(),
    }


def benchmark(request_fn, prompts: list[str], concurrency: int) -> tuple[list[dict], float]:
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(request_fn, prompt) for prompt in prompts]
        results = [future.result() for future in futures]
    wall_s = time.perf_counter() - started
    return results, wall_s


def print_results(results: list[dict], wall_s: float, concurrency: int) -> None:
    first_stream = [float(row["first_stream_ms"]) for row in results]
    totals = [float(row["total_ms"]) for row in results]
    for index, row in enumerate(results, start=1):
        print(
            f"request_{index}: first_stream_ms={row['first_stream_ms']:.1f} "
            f"total_ms={row['total_ms']:.1f} answer={row['answer']!r}"
        )
    print(f"concurrency: {concurrency}")
    print(f"p95_first_stream_ms: {p95(first_stream):.1f}")
    print(f"p95_end_to_end_ms: {p95(totals):.1f}")
    print(f"requests_per_second: {len(results) / wall_s:.3f}")
    print(
        "metric_note: first_stream_ms is client-observed time to the first decoded "
        "text chunk; it is not claimed to be server-native token-level TTFT"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="0 chooses an unused local port")
    parser.add_argument("--requests", type=int, default=6)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--max-new-tokens", type=int, default=48)
    parser.add_argument(
        "--demo-readiness-failure",
        action="store_true",
        help="after the normal fallback benchmark, inject one worker failure and verify readiness becomes 503",
    )
    parser.add_argument(
        "--openai-base-url",
        help="benchmark an existing OpenAI-compatible server such as vLLM instead of the fallback server",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("VLLM_API_KEY"),
        help="optional bearer token for the OpenAI-compatible endpoint",
    )
    args = parser.parse_args()
    if args.requests < 1:
        raise SystemExit("--requests must be at least 1")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be at least 1")
    if args.max_new_tokens < 1 or args.max_new_tokens > 256:
        raise SystemExit("--max-new-tokens must be between 1 and 256")

    base_prompts = [
        "In one sentence, explain time to first token.",
        "Name one reason readiness differs from liveness.",
        "Why can p95 latency matter more than the mean?",
        "What does a deployment model revision identify?",
        "Why should a server bound max_new_tokens?",
        "Why can higher concurrency increase queueing?",
    ]
    prompts = [base_prompts[i % len(base_prompts)] for i in range(args.requests)]

    if args.openai_base_url:
        print(f"backend: openai-compatible")
        print(f"server_url: {args.openai_base_url}")
        print(f"model_id: {args.model}")
        request_fn = lambda prompt: openai_request(
            args.openai_base_url,
            args.model,
            prompt,
            args.max_new_tokens,
            args.api_key,
        )
        results, wall_s = benchmark(request_fn, prompts, args.concurrency)
        print_results(results, wall_s, args.concurrency)
        print("PASS: external serving-runtime evidence captured")
        return

    runtime = ModelRuntime(args.model)
    server = ThreadingHTTPServer((args.host, args.port), handler_for(runtime))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base_url = f"http://{host}:{port}"

    try:
        live_status, live = fetch_json(base_url + "/health/live")
        ready_before_status, ready_before = fetch_json(base_url + "/health/ready")
        print("backend: fallback-transformers")
        print(f"server_url: {base_url}")
        print(f"model_id: {args.model}")
        print(f"device: {runtime.device}")
        print(f"liveness_before_load: status={live_status} body={live}")
        print(f"readiness_before_load: status={ready_before_status} body={ready_before}")

        load_started = time.perf_counter()
        runtime.load()
        load_ms = (time.perf_counter() - load_started) * 1000
        ready_after_status, ready_after = fetch_json(base_url + "/health/ready")
        print(f"model_load_ms: {load_ms:.1f}")
        print(f"readiness_after_load: status={ready_after_status} body={ready_after}")

        request_fn = lambda prompt: local_request(base_url, prompt, args.max_new_tokens)
        results, wall_s = benchmark(request_fn, prompts, args.concurrency)
        print_results(results, wall_s, args.concurrency)
        print(
            "fallback_note: generation is serialized intentionally; compare this queueing "
            "behavior with an OpenAI-compatible serving runtime using --openai-base-url"
        )

        if args.demo_readiness_failure:
            runtime.fail_next_generation = True
            try:
                local_request(base_url, "Trigger the readiness failure demo.", 8)
            except RuntimeError as error:
                print(f"injected_generation_failure: {error}")
            else:
                raise RuntimeError("readiness failure demo did not produce a generation error")
            failed_ready_status, failed_ready = fetch_json(base_url + "/health/ready")
            print(
                "readiness_after_generation_failure: "
                f"status={failed_ready_status} body={failed_ready}"
            )
            if failed_ready_status != 503 or failed_ready.get("ready") is not False:
                raise RuntimeError("runtime failure did not transition readiness to 503")
            print("PASS: runtime failure changed readiness to 503")

        print("PASS: fallback real-model serving evidence captured")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
