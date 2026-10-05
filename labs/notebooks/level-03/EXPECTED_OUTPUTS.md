# Expected outputs — Level 3 Stage B

Values below are representative for seed 13. Compatible library builds can differ slightly; assertions use broad thresholds and qualitative relationships.

## lab-l03-11
- source accuracy > 0.80
- frozen-transfer target accuracy > 0.75
- scratch target accuracy is reported on the same validation set
- incompatible hidden width raises a visible state-dict shape mismatch
- deliberately offset preprocessing creates a substantial feature shift

Representative transfer comparison: source ≈ 0.882, frozen ≈ 0.847, scratch ≈ 0.824.

## lab-l03-12
- frozen target accuracy > 0.75
- conservative fine-tuning moves encoder parameters
- aggressive learning rate moves the encoder substantially farther

Representative: conservative movement ≈ 0.196; aggressive movement ≈ 8.987.

## lab-l03-13
- clean sequence trend accuracy = 1.0
- reversed-order sequence accuracy = 0.0
- deterministic image noise does not improve the clean score

## lab-l03-14
- scratch, frozen, and fine-tuned strategies all exceed 0.75 target accuracy
- frozen transfer has fewer trainable parameters than scratch/fine-tuning
- strategy choice is based on quality plus adaptation/reproducibility evidence
