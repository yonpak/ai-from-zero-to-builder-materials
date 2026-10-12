# p11 bounded-agent reference

The reference implementation is provider-neutral and uses only Python's standard library.

Validate the passing reference:

```bash
python projects/tests/l11/validate_submission.py \
  projects/reference/l11/reference_solution.py \
  projects/reference/l11/sample-run/agent-run.json
```

The final marker should be:

```text
PASS: p11-bounded-agent objective checks
```

The intentional failure fixture keeps task outcomes intact while introducing an unauthorized refund, mismatched approval, a continued repeated-action loop, and a prohibited memory write. It must be rejected:

```bash
python projects/tests/l11/validate_submission.py \
  projects/reference/l11/reference_solution.py \
  projects/reference/l11/failure-run/agent-run.json
```

This command should return non-zero.
