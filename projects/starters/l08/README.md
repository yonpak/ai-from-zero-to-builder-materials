# p08-adapt-small-llm — Adapt a Small LLM

## Goal

Build a reproducible model-adaptation package that can answer:

```text
Why adapt?
→ which data?
→ which split/template?
→ which base?
→ which LoRA/PEFT configuration?
→ which adapter?
→ how would RLHF-style and DPO-style preference optimization differ here?
→ which measured signals are only proxies?
→ what independent evaluation supports the claim?
→ what improved?
→ what regressed?
→ does the run meet the declared release rule?
```

## Prerequisites

Complete Level 8 through **Fine-Tuning Integration Workshop**. The cumulative project dependency is **Reliable LLM Workflow**.

## Canonical reduced path

The repository acceptance path uses Python 3.11+ standard-library code and recorded evidence. It does **not** pretend to measure live LLM quality.

Run:

```bash
python projects/tests/l08/validate_submission.py \
  projects/starters/l08/adaptation.py \
  path/to/your/adaptation-run.json
```

Expected success marker:

```text
PASS: p08-adapt-small-llm objective checks
```

## Complete these TODOs

1. `lora_parameter_count`
2. `group_split`
3. `release_decision`
4. `validate_run`

## Required run record

Your `adaptation-run.json` must record:

- declared behavioral gap;
- base model ID and parent lineage;
- dataset ID, split ID, and template version;
- adaptation method/configuration;
- adapter ID and its declared compatible base;
- target before/after metric;
- retention before/after metric;
- predeclared minimum gain and maximum allowed retention drop;
- critical regression count;
- release decision;
- preference-method context: whether the run uses no preference route, an RLHF-style route, or a DPO-style route;
- a structured route contract where `rlhf_style = reward-model-plus-policy-optimization` and `dpo_style = direct-preference-objective`;
- the selected `optimization_route`, which must agree with `selected_route`;
- `proxy_metric_id`: empty when no preference route is used, otherwise the preference/reward objective being optimized;
- `independent_evaluation_ids`, including the actual target and retention metric IDs and kept separate from any proxy metric;
- a concise explanation of RLHF-style reward-signal + policy optimization versus DPO-style direct preference optimization;
- why the measured preference/reward signal is only a proxy and how the linked independent evaluations support the claim;
- model-card intended use and limitations;
- one failure → evidence → hypothesis → focused fix → result trace.

## Optional real LoRA/QLoRA path

You may add a real fine-tuning run with a small public model when compute is available.

If you do:

- do not commit credentials;
- record exact base revision and tokenizer/template;
- record package versions and hardware/runtime;
- record dataset/split identity;
- record LoRA rank/alpha/target modules and quantization settings;
- preserve before/after target and retention evaluation;
- keep the deterministic reduced path runnable for reviewers.

A successful live run does not replace the acceptance evidence. It extends it.

## Project report

Add `PROJECT_REPORT.md` explaining:

- why fine-tuning was chosen instead of prompting/retrieval/application logic;
- dataset quality and leakage controls;
- adaptation configuration and parameter count;
- before/after target evidence;
- retention/forgetting evidence;
- RLHF-style versus DPO-style route explanation, even when the reduced path uses neither route;
- why preference/reward fit would not replace independent target, retention, factuality, or safety evaluation;
- release decision;
- model-card limitations and next test.

The project is complete when another person can reproduce the declared decision and identify exactly which base, data, adapter, and evaluations support it.

A full PPO implementation is **not** required for this project. The requirement is to explain the optimization routes correctly and encode enough structure for the validator to distinguish them: the selected route must map to the correct optimization path, and any preference/reward proxy ID must remain distinct from the recorded target and retention evaluation IDs.
