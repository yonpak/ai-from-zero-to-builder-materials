# p10 reference package

`reference_solution.py` implements the provider-neutral reduced workflow used by the objective validator.

- `sample-run/tool-run.json` is the passing fixed trace set.
- `failure-run/tool-run.json` intentionally records an unauthorized refund/approval mismatch and must be rejected.

Run:

```bash
python projects/tests/l10/test_reference.py
```
