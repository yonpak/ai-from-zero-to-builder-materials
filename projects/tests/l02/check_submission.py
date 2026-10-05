import importlib.util
from pathlib import Path
import sys
import numpy as np

if len(sys.argv) != 2:
    raise SystemExit("Usage: python projects/tests/l02/check_submission.py <submission-directory>")

submission = Path(sys.argv[1]).resolve()
module_path = submission / "network.py"
if not module_path.exists():
    raise SystemExit(f"Missing {module_path}")

spec = importlib.util.spec_from_file_location("l02_submission", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([[0.0], [1.0], [1.0], [0.0]])

model = module.TinyNetwork(seed=7)
probs = model.forward(X)
expected_shapes = {"W1": (2, 4), "b1": (4,), "W2": (4, 1), "b2": (1,)}
for name, shape in expected_shapes.items():
    actual = getattr(model, name).shape
    if actual != shape:
        raise SystemExit(f"FAIL shape: {name} expected {shape}, got {actual}")
if probs.shape != (4, 1):
    raise SystemExit(f"FAIL output shape: expected (4, 1), got {probs.shape}")

start_loss = model.loss(y)
for _ in range(2000):
    model.forward(X)
    model.backward_and_step(y, learning_rate=0.2)
model.forward(X)
end_loss = model.loss(y)
predictions = model.predict(X).reshape(-1)

if not np.isfinite(end_loss):
    raise SystemExit("FAIL loss is not finite")
if end_loss >= 0.20:
    raise SystemExit(f"FAIL end loss {end_loss:.6f} is not below 0.20")
if not np.array_equal(predictions, np.array([0, 1, 1, 0])):
    raise SystemExit(f"FAIL predictions: {predictions.tolist()}")

print(f"PASS start_loss={start_loss:.6f} end_loss={end_loss:.6f} predictions={predictions.tolist()}")
