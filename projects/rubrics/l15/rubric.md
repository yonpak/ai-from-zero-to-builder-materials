# p15-ai-product-capstone rubric

Total: 100 points.

- **Regression evaluation — 15:** important cases, slices, and critical regressions are represented and recomputed from raw case outcomes.
- **Human evaluation — 10:** rating evidence preserves observable scores and meaningful disagreement rather than only a final average.
- **Authorization and agent security — 15:** trusted principal state controls side effects; generated identity claims cannot expand authority.
- **Privacy, governance, and retention — 15:** retention and hold logic is explicit, deterministic, and checked from raw record fields.
- **Threat modeling and red-team evidence — 15:** severity-aware adversarial tests preserve both blocked paths and critical control failures.
- **Frontier and research evidence — 15:** claims are scoped, dated, versioned, and paired with reproducible local evidence or explicit limitations.
- **Release reasoning — 10:** thresholds and zero-tolerance gates remain independent and the final release decision is recomputed.
- **Reproducibility and communication — 5:** offline acceptance, synthetic fixtures, environment metadata, and reviewable evidence are documented.

Full credit requires independent recomputation of critical metrics and release status. A high aggregate quality score cannot compensate for a zero-tolerance authorization, retention, or critical threat violation.

## Self-check before you call it done

- Can you recompute regression results and inspect individual human-rating scores and disagreement rather than only averages?
- Can you show trusted-principal authorization, retention/hold decisions, and adversarial blocked/failing traces?
- Can you cite dated, versioned frontier claims with local evidence and explicit limitations?
- Can you reproduce independent release gates and explain why no aggregate score can override critical authorization, privacy, or threat failures?
