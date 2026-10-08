# Ship, Evaluate, and Defend an AI Product

Build the required release-evidence controller, then optionally run a separate learner-built real RAG pipeline.

## Implement

Complete the required TODO functions in `capstone.py`:

1. regression and critical-case summaries;
2. human-review mean and disagreement evidence;
3. tool authorization using trusted principal state;
4. retention/deletion eligibility;
5. severity-aware threat-test summaries that preserve threat categories;
6. dated frontier-claim validation;
7. research-reproduction record validation;
8. artifact license/provenance and governance-obligation evidence summaries, including missing required inventory entries;
9. multi-dimensional release gates that include those evidence metrics;
10. raw-evidence run validation, ISO-dated evidence checks, and release-decision recomputation.

The required acceptance path is deterministic and offline. It does not require a live model, provider API, network connection, GPU, cloud account, real user data, or secret.

Run:

```bash
python projects/tests/l15/validate_submission.py \
  projects/starters/l15/capstone.py \
  projects/tests/l15/fixtures/passing/capstone-run.json
```

## Optional real-product extension

Keep this extension separate from the required release controller. Its goal is to make one real RAG path visible: retrieval uses a real embedding model, generation uses a real instruction-tuned model, the model returns a small structured claim, application code checks it, and verified values are rendered into user-facing prose.

Complete `product.py`, then run the lightweight contract check before downloading model weights:

```bash
pip install -r labs/real-model/requirements.txt
python projects/tests/l15/validate_product.py \
  projects/starters/l15/product.py
```

Then run the real pipeline:

```bash
python labs/real-model/l15_capstone_real_app.py \
  --product projects/starters/l15/product.py
```

You may pin model revisions with `--embedding-revision` and `--generator-revision` when you want a more reproducible experiment.

The harness supplies the corpus, embedding model, tokenizer, and generator. For observability, the real run calls your `retrieve()`, `build_grounded_messages()`, and `generate_grounded_claim()` stages separately, so completed retrieval evidence is still visible if a later generation step fails. The lightweight contract checker separately verifies that your `answer_question()` orchestrates those same stages in order. The harness also wraps the models so it can report whether `encode()` and `generate()` returned successfully for each case.

The pipeline returns three pieces with different origins:

```text
hits        -> retrieval output
claim       -> generator output
source_ids  -> generator-declared evidence
```

The fixed examples use these small claim shapes. The values must come from retrieved evidence:

```text
warranty length  -> {"warranty_months": <integer>}
factory reset    -> {"action": <string>, "control": <string>, "seconds": <integer>}
reset + warranty -> {"reset_changes_warranty": <boolean>}
```

The script prints the expected claim beside the model claim. A wrong model claim is an observation to inspect, not a release decision. The report distinguishes whether generation was not run, raised an error, or returned a value, then checks whether that returned value is a structured object with the expected claim/source field types. The model-call counters only count calls that return successfully. If the claim and source match, application code renders the final answer from those checked values. Otherwise, no answer is rendered.

The output report is written to `artifacts/real-model/l15-real-rag-run.json`. It is an experiment trace, not a capstone release record.


## Docker bridge

The included Dockerfile provides a reproducible Python environment for the Docker-oriented final Labs. The objective acceptance path remains the standard-library Python checks above so evaluation logic can be distinguished from container, network, model-provider, or hardware setup problems.

## Evidence boundary

Use only synthetic fixtures in the required project path. Do not add real credentials, personal data, production secrets, or destructive actions. A passing release record means the candidate satisfies the declared tests and gates under the recorded evidence snapshot; it is not a claim of universal safety.
