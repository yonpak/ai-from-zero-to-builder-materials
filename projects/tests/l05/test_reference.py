import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from failure_fixture import expect_rejected, mutated_copy

repo_root = pathlib.Path(__file__).resolve().parents[3]
validator = repo_root / "projects/tests/l05/validate_submission.py"
reference = repo_root / "projects/reference/l05/reference_solution.py"
result = subprocess.run([sys.executable, str(validator), str(reference)], check=True, capture_output=True, text=True)
assert "PASS: p05-mini-transformer objective checks" in result.stdout
print("PASS: p05 reference solution satisfies objective validator")


with mutated_copy(
    reference,
    (
        "legal_keys = [split[k_index][h] for k_index in range(q_index + 1)]",
        "legal_keys = [split[k_index][h] for k_index in range(len(split))]",
    ),
) as broken:
    expect_rejected(
        [validator, broken],
        "p05 causal attention can see future tokens",
    )
