# Rubric — p02-neural-net-from-scratch

Total: 100 points. The project measures the Level 2 exit skills directly.

| Criterion | Points | Observable evidence |
|---|---:|---|
| Functional network | 25 | Two-layer NumPy network runs, preserves required shapes, reduces loss, and predicts XOR correctly under the documented seed/configuration. |
| Shapes and forward reasoning | 15 | Report names parameter/activation shapes and explains the forward path without relying on a framework abstraction. |
| Backpropagation and gradient reasoning | 20 | Backward implementation has gradients matching parameter shapes; report explains the chain from loss to parameters and includes a hand or finite-difference check. |
| Training choices | 10 | Learner explains batch choice, learning rate, and update rule; changes are reproducible. |
| Debugging | 15 | Learner creates the approved large-learning-rate failure or an equivalent intentional failure, records evidence, forms a hypothesis, fixes it, and verifies the result. |
| Evaluation and regularization reasoning | 5 | Learner distinguishes training objective from generalization and identifies one sensible way to detect or reduce overfitting. |
| Reproducibility | 5 | Seed/configuration are recorded; project runs from a clean start; checker output is included. |
| Communication | 5 | Explanation is clear, uses the learner's own words, and connects nonlinearity, gradients, and training evidence. |

## Performance anchors
### Full credit
The implementation works and the explanations make cause and effect traceable. Debugging evidence shows the learner can locate a failure rather than only copy a fix.

### Partial credit
The network mostly works but one exit skill is weak—for example, shapes are correct but gradient reasoning is vague, or the failure is repaired without showing evidence.

### Insufficient
The submission relies on a high-level trainer/framework to hide the first-principles work, changes the canonical task, cannot reproduce its result, or presents only final predictions without explaining computation and debugging.
