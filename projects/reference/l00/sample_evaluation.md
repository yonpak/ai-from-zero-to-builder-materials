# p00-data-detective sample evaluation

This example demonstrates rubric use; learner output does not need to match it byte-for-byte.

## Observed evidence
- Objective validator: PASS.
- Threshold chosen from training examples: `4`.
- Clean held-out mistakes: model `0`, majority baseline `2`.
- Intentional noisy held-out scenario: `1` model mistake.
- Debug note identifies the input `3` case, proposes label noise or missing information as hypotheses, and does not retune the clean threshold on the noisy test answer.
- Explanation states that the measured improvement applies to this small held-out set and does not claim universal accuracy.

## Rubric application
| Criterion | Score | Evidence |
| --- | ---: | --- |
| Features and labels | 20/20 | Roles are explicit in code and explanation. |
| Train/test separation | 20/20 | Threshold is selected from training examples only. |
| Predictor and baseline | 20/20 | Validator passes; same held-out rows and metric are used. |
| Failure/debugging | 17/20 | Failure is isolated and hypothesis is evidence-based; a second follow-up check could be more specific. |
| Reproducibility/communication | 18/20 | Standard-library command is reproducible and limitation is stated; experiment note could record Python version explicitly. |
| **Total** | **95/100** | Ready to advance. |

## Example feedback
The implementation demonstrates all Level 0 exit skills and uses the test set correctly. The next improvement is not a larger model; it is a clearer follow-up experiment for the noisy example, such as checking whether the label is trustworthy or whether another feature is missing.
