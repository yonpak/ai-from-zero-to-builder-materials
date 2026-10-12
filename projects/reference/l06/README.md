# p06 Reference Evaluation Assets

`reference_solution.py` demonstrates the deterministic reduced-path utility behavior. `sample-run/run.json` is a small example of acceptable packaging/evaluation evidence; it is not a claim that the generated strings are a quality target.

Run:

```bash
python projects/tests/l06/test_reference.py
python projects/tests/l06/validate_submission.py \
  projects/reference/l06/reference_solution.py \
  projects/reference/l06/sample-run/run.json
python labs/notebooks/level-06/l06-13-package-run.py projects/reference/l06/sample-run
python labs/notebooks/level-06/l06-14-integration-check.py projects/reference/l06/sample-run
```

Intentional failure:

```bash
python labs/notebooks/level-06/l06-14-integration-check.py projects/reference/l06/failure-run
```

The final command must fail with a tokenizer/checkpoint fingerprint mismatch. The correct response is to repair the artifact pairing/metadata source, not to weaken the validation rule.
