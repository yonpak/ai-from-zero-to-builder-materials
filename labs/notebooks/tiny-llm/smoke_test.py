from pathlib import Path
import torch

from tiny_llm import (
    SimpleTokenizer,
    TinyConfig,
    TinyDecoderLM,
    causal_attention,
    count_parameters,
    future_attention_mass,
    set_seed,
    train_steps,
)

HERE = Path(__file__).resolve().parent
text = (HERE / "tiny_corpus.txt").read_text(encoding="utf-8")

set_seed(7)
tokenizer = SimpleTokenizer.from_text(text)
ids = tokenizer.encode(text)
assert tokenizer.vocab_size > 20
assert len(ids) > 400
assert tokenizer.encode("zzzxxyy") == [0]

q = torch.eye(4).unsqueeze(0)
out, weights = causal_attention(q, q, q)
assert out.shape == q.shape
assert future_attention_mass(weights) == 0.0
assert torch.allclose(weights.sum(dim=-1), torch.ones_like(weights.sum(dim=-1)))

config = TinyConfig(vocab_size=tokenizer.vocab_size, block_size=8, n_embd=32, n_head=4, n_layer=1)
model = TinyDecoderLM(config)
x = torch.tensor([ids[:8]], dtype=torch.long)
y = torch.tensor([ids[1:9]], dtype=torch.long)
logits, loss = model(x, y)
assert logits.shape == (1, 8, tokenizer.vocab_size)
assert loss is not None and torch.isfinite(loss)
assert count_parameters(model) < 100_000

losses = train_steps(model, ids, steps=40, batch_size=8, learning_rate=5e-3, seed=7)
assert min(losses[-10:]) < losses[0]

prompt = torch.tensor([tokenizer.encode("the moon")], dtype=torch.long)
sample_a = model.generate(prompt, 12, temperature=0.8, top_k=6, seed=11)
sample_b = model.generate(prompt, 12, temperature=0.8, top_k=6, seed=11)
assert torch.equal(sample_a, sample_b)
assert sample_a.shape[1] == prompt.shape[1] + 12

print({
    "vocab_size": tokenizer.vocab_size,
    "parameter_count": count_parameters(model),
    "initial_loss": round(losses[0], 4),
    "best_last_10_loss": round(min(losses[-10:]), 4),
    "sample": tokenizer.decode(sample_a[0].tolist()),
})
