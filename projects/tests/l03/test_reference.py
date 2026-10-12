import importlib.util
import pathlib
import unittest
import sys

HERE = pathlib.Path(__file__).resolve().parent
REFERENCE = HERE.parents[1] / "reference" / "l03" / "adaptation_reference.py"
spec = importlib.util.spec_from_file_location("adaptation_reference", REFERENCE)
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)


sys.path.insert(0, str(HERE.parent))
from failure_fixture import expect_rejected, mutated_copy

class TransferReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = ref.run_reference()

    def test_quality_thresholds(self):
        self.assertGreater(self.metrics["source_accuracy"], 0.80)
        self.assertGreater(self.metrics["scratch_accuracy"], 0.75)
        self.assertGreater(self.metrics["frozen_accuracy"], 0.75)
        self.assertGreater(self.metrics["fine_accuracy"], 0.75)

    def test_controlled_vs_aggressive_movement(self):
        self.assertGreater(self.metrics["fine_movement"], 0.0)
        self.assertGreater(self.metrics["aggressive_movement"], self.metrics["fine_movement"] * 2)

    def test_noise_slice(self):
        self.assertLess(self.metrics["noisy_accuracy"], self.metrics["fine_accuracy"] + 0.02)

    def test_intentional_failure_fixture_rejects_unfrozen_encoder(self):
        checker = HERE / "check_submission.py"
        with mutated_copy(
            REFERENCE,
            (
                "for p in encoder.parameters(): p.requires_grad=False",
                "for p in encoder.parameters(): p.requires_grad=True",
            ),
            filename="adaptation.py",
        ) as broken:
            expect_rejected(
                [checker, broken.parent],
                "p03 frozen-transfer encoder remains trainable",
                marker="frozen encoder still has trainable parameters",
            )

if __name__ == "__main__":
    unittest.main()
