import importlib.util
from pathlib import Path
import unittest
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "projects" / "reference" / "l02" / "network_reference.py"
spec = importlib.util.spec_from_file_location("l02_reference", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([[0.0], [1.0], [1.0], [0.0]])


sys.path.insert(0, str(ROOT / "projects" / "tests"))
from failure_fixture import expect_rejected, mutated_copy

class ReferenceProjectTests(unittest.TestCase):
    def test_parameter_and_activation_shapes(self):
        model = module.TinyNetwork(seed=7)
        probs = model.forward(X)
        self.assertEqual(model.W1.shape, (2, 4))
        self.assertEqual(model.b1.shape, (4,))
        self.assertEqual(model.W2.shape, (4, 1))
        self.assertEqual(model.b2.shape, (1,))
        self.assertEqual(probs.shape, (4, 1))

    def test_training_reduces_loss_and_solves_xor(self):
        model = module.TinyNetwork(seed=7)
        model.forward(X)
        start = model.loss(y)
        for _ in range(2000):
            model.forward(X)
            model.backward_and_step(y, learning_rate=0.2)
        model.forward(X)
        end = model.loss(y)
        predictions = model.predict(X).reshape(-1)
        self.assertLess(end, 0.20)
        self.assertLess(end, start)
        np.testing.assert_array_equal(predictions, [0, 1, 1, 0])

    def test_gradient_shapes_match_parameters(self):
        model = module.TinyNetwork(seed=7)
        model.forward(X)
        grads = model.backward_and_step(y, learning_rate=0.0)
        self.assertEqual(grads["dW1"].shape, model.W1.shape)
        self.assertEqual(grads["db1"].shape, model.b1.shape)
        self.assertEqual(grads["dW2"].shape, model.W2.shape)
        self.assertEqual(grads["db2"].shape, model.b2.shape)

    def test_intentional_failure_fixture_rejects_wrong_gradient_sign(self):
        checker = ROOT / "projects" / "tests" / "l02" / "check_submission.py"
        with mutated_copy(
            MODULE_PATH,
            ("self.W1 -= learning_rate * dW1", "self.W1 += learning_rate * dW1"),
            filename="network.py",
        ) as broken:
            expect_rejected(
                [checker, broken.parent],
                "p02 hidden-layer update uses the wrong gradient sign",
            )

if __name__ == "__main__":
    unittest.main()
