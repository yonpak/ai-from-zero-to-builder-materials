# Reference / sample evaluation — p02-neural-net-from-scratch

This file demonstrates rubric use. It is not a byte-identical target for learner submissions.

## Reference run
With seed `7`, learning rate `0.2`, and 2000 full-batch updates, the reference implementation reduces binary cross-entropy substantially and predicts all four XOR labels correctly.

## Rubric application example
- **Functional correctness:** Meets. Forward and backward paths preserve expected shapes; loss falls; all XOR cases are classified correctly.
- **Shape and gradient reasoning:** Meets. The implementation exposes `W1 (2,4)`, `b1 (4,)`, hidden activation `(4,4)`, `W2 (4,1)`, and output `(4,1)`, and gradients match those shapes.
- **Debugging:** Meets when the learner documents the large-learning-rate failure with evidence and restores a stable step size.
- **Evaluation:** Meets when start/end loss and final predictions are reported using the fixed dataset without changing labels or hiding examples.
- **Reproducibility:** Meets when seed and learning rate are recorded and the submission checker passes from a clean run.
- **Communication:** Meets when the report explains nonlinearity and backpropagation in the learner's own words.

A submission can earn full credit with different parameter values or intermediate losses if it satisfies the observable anchors in the rubric.
