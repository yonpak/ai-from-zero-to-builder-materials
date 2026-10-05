# Rubric — p03-transfer-learning

Total: 100 points. The project measures the Level 3 exit skills directly.

| Criterion | Points | Observable evidence |
|---|---:|---|
| Representation / transfer reasoning | 15 | Explains what the source encoder learned, why the target task is related, and why transfer is a hypothesis rather than a guarantee. |
| Functional frozen transfer | 15 | Reuses the pretrained encoder, freezes it correctly, trains a new head, and reports reproducible validation evidence. |
| Controlled fine-tuning | 15 | Starts from the same frozen checkpoint, unfreezes the encoder, uses a conservative learning rate, and measures encoder movement. |
| Fair strategy comparison | 15 | Scratch, frozen transfer, and fine-tuning use the same target split, preprocessing, seed policy, validation set, and metric. |
| Failure analysis | 10 | Includes the required noisy-image slice with a precise perturbation definition, seed, clean control, and interpretation. |
| Intentional failure and debugging | 15 | Runs aggressive fine-tuning, records movement/quality evidence, forms a causal hypothesis, restores the correct checkpoint/configuration, and verifies the fix. |
| Reproducibility / provenance | 10 | Records Python/package versions, seed, CPU/GPU condition, dataset provenance, and clean-start/checker evidence; no credentials are required. |
| Communication / decision | 5 | Chooses a strategy using at least three pieces of evidence and names a real tradeoff rather than claiming one method is universally best. |

## Performance anchors

### Full credit
The implementation is reproducible, all three strategies are fairly compared, frozen and fine-tuned behavior are technically correct, and the final decision is supported by metrics, movement, failure slices, and resource/reproducibility evidence.

### Partial credit
The code mostly works but one exit skill is weak—for example, transfer is implemented but the comparison changes the split, or fine-tuning succeeds without measuring movement or debugging the aggressive run.

### Insufficient
The submission changes the canonical task, uses different validation data for each strategy, leaks validation labels into training, treats a pretrained label as proof of quality, cannot reproduce its result, or reports only one overall accuracy.
