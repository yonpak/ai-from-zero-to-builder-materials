# Expected outputs and checks

Run from `labs/notebooks/tiny-llm`:

```bash
python smoke_test.py
```

Expected invariants:

1. tokenizer vocabulary contains more than 20 tokens;
2. unknown text maps to `<unk>` id `0`;
3. causal attention assigns exactly zero probability mass to future positions;
4. the assembled model returns logits shaped `(batch, time, vocab_size)`;
5. the teaching configuration stays below 100,000 parameters;
6. training loss is finite and at least one of the final 10 losses is below the first loss;
7. sampling adds the requested number of tokens;
8. repeated sampling with the same trained model and sampling seed is identical.

The final printed loss/sample text is informative, not a golden string. CPU kernels and PyTorch versions can move the exact decimal values.
