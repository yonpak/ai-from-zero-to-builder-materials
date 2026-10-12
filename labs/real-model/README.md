# Optional real-model and real-protocol labs for Levels 7–15

These exercises are **extensions**, not prerequisites for the required deterministic labs or Level projects.

They connect the course's inspectable toy workflows to real pretrained models, the official MCP SDK at Level 13, a real local inference service at Level 14, and an actual RAG product evidence path at Level 15. The required path remains inexpensive, offline, and reproducible.

## Environment

Use Python 3.10+ in a clean local virtual environment. These are optional experiments: the regular Labs and projects remain offline and deterministic. For default model-backed scripts, allow roughly 1–2 GB for Qwen2.5-0.5B weights and 0.1–0.2 GB for MiniLM embeddings, plus dependencies and caches (plan for **8–12 GB free disk** overall; actual downloads vary by OS/package platform). Cached weights are reused. The MCP client/server exercise needs no model weights. For prerequisite code-reading skills, see [P10 — Python for Real AI Services](https://aizero.ruzincompany.com/learn/12-level-12/python-for-real-ai-services).

### macOS / Linux

From the public learner-materials repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

From the public learner-materials repository root, with Python 3.10+ installed:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If your shell blocks the activation script, open a new PowerShell session and use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` **only for that session**, then activate again. You can also skip activation and use `.\.venv\Scripts\python.exe -m pip ...` plus `.\.venv\Scripts\python.exe labs/real-model/l13_mcp_client.py` directly. Do not change machine-wide execution policy. Model-serving runtimes such as vLLM may require Linux/WSL2 even though the standard-library fallback/client works in PowerShell.

### Choose dependencies for the exercise you actually run

**MCP client/server only (Level 13; no model weights, small install):**

```bash
python -m pip install "mcp>=2,<3"
python labs/real-model/l13_mcp_client.py
```

The MCP SDK is the only dependency from this folder required for that in-process exercise. It still installs its own transitive dependencies. This is the easiest real-protocol starting point.

**HTTP benchmark client only (Level 14; no model libraries in the client):** No `pip install` command is required. Run `python labs/real-model/l14_real_model_serving.py --openai-base-url http://127.0.0.1:8000 --model Qwen/Qwen2.5-0.5B-Instruct --requests 12 --concurrency 4` **only after** you start a compatible server in a separate environment. The server, not the benchmark client, owns its model weights and packages.

**Real-model generation, embeddings, LoRA, local fallback server, or the full integration smoke:** Install the complete requirements:

```bash
python -m pip install -r labs/real-model/requirements.txt
```

These model-backed exercises need download access the first time, and can require substantial RAM, disk and possibly GPU resources. You can start with MCP or the client-only benchmark and install model dependencies later. Windows PowerShell uses the **same** `python -m pip install` commands above after activation.

## Release smoke for the core real integrations

In Windows PowerShell, use the **same single-line** `python labs/real-model/test_real_integrations.py` command shown below (no bash activation needed after the PowerShell setup).

After installing the **full real-model requirements** (not the MCP-only package), run the core model/tool/protocol integrations in one command:

```bash
python labs/real-model/test_real_integrations.py
```

The runner records installed package versions, then verifies:

- Level 13 negotiates with the official MCP SDK, discovers a tool, and returns structured content;
- Level 10 gets a real model-generated tool proposal and reaches validated application execution;
- Level 11 performs at least one controller-owned tool execution inside the bounded loop and then reaches a final answer.

This smoke is intentionally **manual/release-only** rather than part of normal C6 validation because it downloads and loads model weights. The Level 14 serving benchmark and Level 15 real-product capstone are run separately because their outputs are learner-facing performance and release evidence rather than fixed smoke markers. The required course path and PR CI remain deterministic and offline.

To smoke-check the optional dependency environment after installation:

```bash
python - <<'PY'
from importlib.metadata import version
for name in ["torch", "transformers", "peft", "sentence-transformers", "mcp"]:
    print(name, version(name))
PY
```

PowerShell equivalent of the bash heredoc version check above:

```powershell
python -c "from importlib.metadata import version; [print(name, version(name)) for name in ('torch','transformers','peft','sentence-transformers','mcp')]"
```

## Level 7 — prompt a real LLM

```bash
python labs/real-model/l07_prompt_real_model.py
```

Default model: `Qwen/Qwen2.5-0.5B-Instruct`.

Compare a vague prompt with an explicit output/evidence contract, then inspect the deterministic JSON checks performed by application code.

## Level 8 — train a real LoRA adapter

```bash
python labs/real-model/l08_lora_real_model.py --steps 4
```

The script loads the same small causal LM, attaches PEFT LoRA adapters to attention projections, trains only adapter parameters for a few steps, compares a held-out response before/after, and saves the adapter under `artifacts/real-model/`.

A CUDA GPU is recommended. CPU execution is allowed for mechanics inspection but can be slow. A few training steps do **not** establish model-quality improvement; use the Level 8 target and retention evaluations for that claim.

## Level 9 — retrieve with real embeddings

```bash
python labs/real-model/l09_embedding_rag_real_model.py
```

Default embedding model: `sentence-transformers/all-MiniLM-L6-v2`.

The script embeds a tiny corpus and query, performs cosine-equivalent ranking with normalized vectors, and prints source IDs and scores. To also pass retrieved evidence to a real generator:

```bash
python labs/real-model/l09_embedding_rag_real_model.py --generate
```

Keep the retrieved IDs visible so you can distinguish retrieval failure from generation failure.

## Level 10 — real model tool calling

```bash
python labs/real-model/l10_tool_calling_real_model.py
```

The tokenizer receives a real Python tool definition through its chat template. The model proposes a tool call, but application code still validates the allowlist and argument shape before executing it. This is the same trust boundary used by the deterministic Level 10 Labs.

## Level 11 — bounded real-model agent loop

```bash
python labs/real-model/l11_agent_loop_real_model.py --max-steps 3
```

The real model can propose a tool call and consume its result, while application code enforces a maximum step count and repeated-action guard. Try `--max-steps 1` and compare the terminal behavior.

## Level 13 — real MCP server and client

The required Level 13 Lab first practices the protocol boundary deterministically. This extension then uses the official MCP Python SDK.

Run the in-process client/server path:

```bash
python labs/real-model/l13_mcp_client.py
```

The client negotiates MCP, discovers `get_order_status`, calls it, and reads structured content through the official SDK.

To inspect the same server with the MCP development tooling:

```bash
uv run --with "mcp[cli]>=2,<3" mcp dev labs/real-model/l13_mcp_server.py
```

The SDK handles protocol mechanics. Your application still owns capability scope, authorization, side-effect policy, and telemetry.

## Level 14 — serve a real model and measure operations

```bash
python labs/real-model/l14_real_model_serving.py --requests 6 --concurrency 2
```

The fallback script starts a local HTTP service around the instruction-tuned model, exposes separate liveness and readiness checks, sends concurrent requests, and measures client-observed time to first streamed text, p95 end-to-end latency, and requests per second. The fallback deliberately serializes model generation so queueing becomes visible.

For a real serving scheduler, start a vLLM OpenAI-compatible server in a separate environment, then point the same benchmark at it. The benchmark process is only an HTTP client in this mode, so its environment does **not** need `torch`, `transformers`, or the full real-model requirements. A plain Python 3.10+ environment is enough on the measurement side; keep vLLM and its model dependencies in the server environment.

```bash
# server environment
vllm serve Qwen/Qwen2.5-0.5B-Instruct

# separate measurement environment; no torch/transformers required
python labs/real-model/l14_real_model_serving.py \
  --openai-base-url http://127.0.0.1:8000 \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --requests 12 --concurrency 4
```

The client metric is intentionally named `first_stream_ms`: a decoded streaming chunk can contain more than one raw token, so it is not presented as server-native token-level TTFT. Use the serving runtime's own metrics when exact TTFT is required.

To exercise the fallback's failure semantics after a normal small benchmark:

```bash
python labs/real-model/l14_real_model_serving.py \
  --requests 2 --concurrency 1 --demo-readiness-failure
```

The injected worker failure must produce a stream error, mark the runtime not ready, and make the next `/health/ready` request return 503.

## Level 15 — run a real RAG pipeline

The required Level 15 capstone stays deterministic and offline. This optional extension has a smaller job: run one learner-built RAG path with real models and inspect where retrieval or generation succeeds or fails.

First check the learner product contract without downloading model weights:

```bash
python projects/tests/l15/validate_product.py \
  projects/starters/l15/product.py
```

Then run:

```bash
python labs/real-model/l15_capstone_real_app.py \
  --product projects/starters/l15/product.py
```

The harness loads a real sentence-embedding model and a real instruction-tuned generator. It executes your retrieval, grounding, and generation functions as separate stages so evidence from a completed stage is preserved when a later stage fails. The lightweight product checker separately verifies that `answer_question()` orchestrates those same stages. Small wrappers count successful returns from `encode()` and `generate()`, and returned retrieval rows must match rows from the supplied corpus.

For every fixed question the script shows:

```text
Question
Retrieved source IDs
Expected structured claim
Model structured claim
Real embedder called: true/false
Real generator called: true/false
Generation status: not_run/error/returned
Structured output object valid: true/false
Structured output shape valid: true/false
Claim match: true/false
Source match: true/false
Rendered answer or <not rendered>
```

A model-quality miss does not become a Level 15 release failure. It is evidence for diagnosis: retrieval may have missed the needed source, generation may have failed before returning, a returned value may not be a JSON object with the expected field types, or the source declaration may not match. The report distinguishes whether generation was not run, raised an error, or returned a value. The call counters increase only after the underlying model call returns successfully. The required capstone separately teaches how release evidence and release gates work.

The run writes `artifacts/real-model/l15-real-rag-run.json`. Treat that file as an experiment trace, not as a release record.


## PowerShell commands for multi-line examples

Bash uses `\` to continue a command; PowerShell uses a backtick, which can be easy to omit. These **one-line** equivalents avoid shell-specific continuations:

```powershell
python labs/real-model/l09_embedding_rag_real_model.py --generate
python labs/real-model/l11_agent_loop_real_model.py --max-steps 3
python labs/real-model/l14_real_model_serving.py --requests 6 --concurrency 2
python labs/real-model/l14_real_model_serving.py --requests 2 --concurrency 1 --demo-readiness-failure
python labs/real-model/l14_real_model_serving.py --openai-base-url http://127.0.0.1:8000 --model Qwen/Qwen2.5-0.5B-Instruct --requests 12 --concurrency 4
python projects/tests/l15/validate_product.py projects/starters/l15/product.py
python labs/real-model/l15_capstone_real_app.py --product projects/starters/l15/product.py
```

To try the SDK development tool on Windows after installing `uv`, use `uv run --with "mcp[cli]>=2,<3" mcp dev labs/real-model/l13_mcp_server.py`. For actual benchmarking, start the external serving runtime separately as documented above; the `--openai-base-url` command does not launch one.

## Model and library references

- Qwen2.5-0.5B-Instruct: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
- Transformers tool-use documentation: https://huggingface.co/docs/transformers/main/chat_extras
- Sentence Transformers all-MiniLM-L6-v2: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- PEFT LoRA documentation: https://huggingface.co/docs/peft/main/en/quicktour
- Official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk

You may substitute another compatible model with the command-line flags. Pin model revisions when you need a reproducible experiment.
