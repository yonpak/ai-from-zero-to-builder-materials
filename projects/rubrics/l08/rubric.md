# p08-adapt-small-llm Rubric — Adapt a Small LLM

Score each criterion from **0–4**. A submission should score at least **16/20** overall and must not score 0 on data boundaries, adaptation lineage, or evaluation.

| Criterion | 4 — Strong evidence | 3 — Meets | 2 — Partial | 1 — Weak | 0 — Missing |
|---|---|---|---|---|---|
| Adaptation decision | Measured behavioral gap; prompting/retrieval/application alternatives considered; fine-tuning choice is evidence-based | Clear fine-tuning rationale with small omissions | Rationale exists but alternatives/evidence are shallow | Fine-tuning chosen mainly because it is available | No adaptation rationale |
| Data and split integrity | Provenance, grouping, dedup/conflict policy, formatting version, and train/eval separation are reproducible | Data pipeline is reproducible with minor gaps | Some provenance/split evidence missing | Dataset dump with weak leakage controls | No trustworthy data boundary |
| PEFT/LoRA implementation and lineage | Rank/count/targets/base compatibility are correct and all artifacts identify their parents | Correct adapter implementation/config with minor gaps | Adapter works but identity/count evidence incomplete | Adapter exists with unclear base/config | No coherent adaptation artifact |
| Before/after, retention, and preference-context evaluation | Paired target and retention suites, predeclared thresholds, regression IDs, and release decision are supported; RLHF-style vs DPO-style routes are distinguished; preference/reward signals are explicitly separated from independent quality evidence | Complete evaluation and preference-method explanation with minor gaps | Target evaluation present but retention, route distinction, or proxy-vs-independent evidence is weak | Cherry-picked generations, training loss, or preference/reward score treated as sufficient quality evidence | No held-out adaptation evaluation |
| Documentation and reproducibility | Training record, model card, limitations, debug trace, commands, and optional live-run differences are explicit | Reproducible package with small omissions | Important versions/limitations missing | Mostly screenshots or output dumps | No reproducible package |

## Objective checks

The reduced validator checks:

- LoRA parameter-count arithmetic;
- group-safe train/validation splitting;
- target-gain and retention-drop release rules;
- zero critical-regression requirement;
- base/adapter lineage;
- required dataset/adaptation/evaluation identities;
- a structured RLHF-style vs DPO-style route contract and selected optimization route;
- proxy metric identity when a preference route is used;
- independent-evaluation IDs linked to the recorded target and retention metrics and separated from the proxy metric;
- model-card limitations;
- intentional failure rejection.

## Judgment questions

Ask yourself, and point to a record before answering yes:

- Does the measured gap justify fine-tuning over prompting, retrieval, or application changes? If not, revisit the decision.
- Does the target dataset represent the desired behavior? If not, document the mismatch.
- Have you distinguished reward-model/policy optimization (RLHF-style) from direct preference optimization (DPO-style)? If not, correct the route description.
- Have you avoided treating preference, reward, or SFT proxies as broad truth or quality? If not, narrow the claim.
- Do measured target gains justify retention regressions under the stated release rule? If not, record a no-release decision.
- Do the limitations mark the boundary of tested evidence? If not, add specific excluded cases.

## Assessment guardrail

A live GPU fine-tune is optional for repository acceptance. If provided, it extends the evidence but does not replace the deterministic reduced path or the requirement for before/after retention evaluation.

## Self-check before you call it done

- Can you support the adaptation choice with a measured gap and alternatives to fine-tuning?
- Can you trace data provenance, grouping/splits, LoRA configuration, and base-to-adapter lineage?
- Can you point to paired target/retention metrics, independent evaluation IDs, critical regressions, and the release decision?
- Can you distinguish preference/reward proxy evidence from independent quality and document a debug trace, model-card limits, and reproducibility?
