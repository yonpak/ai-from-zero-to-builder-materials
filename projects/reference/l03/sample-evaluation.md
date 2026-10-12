# Sample evaluation — p03-transfer-learning

This example applies the rubric to the reference implementation. Learner output does not need to match these floating-point values byte-for-byte.

## Reference evidence

- Source digit classifier validation accuracy: about **0.882**.
- Scratch target accuracy: about **0.824**.
- Frozen-transfer target accuracy: about **0.847**.
- Conservative fine-tuned target accuracy: about **0.853**.
- Conservative encoder movement: about **0.196** in L2 norm.
- Aggressive (`lr=1.0`) encoder movement: about **8.987** with lower target accuracy (about **0.787**).
- Noisy-image slice accuracy for the fine-tuned model: about **0.782**, below the clean score.

## Example rubric application

| Criterion | Example score | Reason |
|---|---:|---|
| Representation / transfer reasoning | 15/15 | Source and target relationship is explicit and transfer is compared with scratch. |
| Functional frozen transfer | 15/15 | Encoder is copied, frozen, unchanged during head training, and exceeds the target threshold. |
| Controlled fine-tuning | 15/15 | Fine-tuning starts from the frozen checkpoint and records parameter movement. |
| Fair strategy comparison | 15/15 | Split, preprocessing, seed, validation set, and metric are shared. |
| Failure analysis | 10/10 | Noisy-image slice is deterministic and compared with a clean control. |
| Intentional failure / debugging | 15/15 | Aggressive learning rate produces much larger movement and worse validation evidence. |
| Reproducibility / provenance | 10/10 | CPU-first, fixed seed, bundled dataset, explicit package ranges, no credentials. |
| Communication / decision | 5/5 | Frozen transfer is defensible when its small trainable surface matters; fine-tuning is defensible when the small quality gain is worth the extra adaptation surface. |

**Example total: 100/100.**

The reference does not imply that fine-tuning is always the correct strategy. The learner must defend a choice under the observed constraints.
