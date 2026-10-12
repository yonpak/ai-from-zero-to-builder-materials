# p15-ai-product-capstone reference

The reference implementation validates a synthetic AI-product release record without external services.

Passing evidence recomputes to:

```text
regression_success: 1.0
critical_regressions: 0
human_mean_score: 4.333
high_disagreement_cases: 0
unauthorized_actions: 0
retention_violations: 0
critical_threat_failures: 0
frontier_evidence_violations: 0
reproduction_evidence_violations: 0
release_passed: true
```

The intentional failure fixture contains one critical regression, one high-disagreement human-review case, one unauthorized execution, one retention violation, one critical threat-test failure, one frontier-evidence violation, and one invalid reproduction conclusion. Its release flag is false and the validator must reject it.
