"""Small decoder-only language model used by the C8 Tiny LLM vertical slice.

The implementation is intentionally compact and framework-light: PyTorch supplies tensors,
autograd, and modules, while the tokenizer, causal mask, attention, block composition,
training loop, and sampling are visible in this file.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
import re
from typing import Iterable

import torch
from torch import nn
import torch.nn.functional as F


TOKEN_PATTERN = re.compile(r"[A-Za-z]+|[0-9]+|[^\w\s]")


def set_seed(seed: int = 7) -> None:
    """Seed Python and PyTorch for repeatable CPU teaching runs."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class SimpleTokenizer:
    """A deterministic lowercase word-and-punctuation tokenizer."""

    def __init__(self, vocab: Iterable[str] | None = None) -> None:
        self.itos = list(vocab or ["<unk>"])
        if not self.itos or self.itos[0] != "<unk>":
            raise ValueError("vocab index 0 must be <unk>")
        self.stoi = {token: i for i, token in enumerate(self.itos)}

    @staticmethod
    def split(text: str) -> list[str]:
        return TOKEN_PATTERN.findall(text.lower())

    @classmethod
    def from_text(cls, text: str) -> "SimpleTokenizer":
        tokens = cls.split(text)
        vocab = ["<unk>", *sorted(set(tokens))]
        return cls(vocab)

    def encode(self, text: str) -> list[int]:
        return [self.stoi.get(token, 0) for token in self.split(text)]

    def decode_tokens(self, ids: Iterable[int]) -> list[str]:
        return [self.itos[int(i)] if 0 <= int(i) < len(self.itos) else "<unk>" for i in ids]

    def decode(self, ids: Iterable[int]) -> str:
        tokens = self.decode_tokens(ids)
        text = " ".join(tokens)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        return text

    @property
    def vocab_size(self) -> int:
        return len(self.itos)


@dataclass(frozen=True)
class TinyConfig:
    vocab_size: int
    block_size: int = 12
    n_embd: int = 48
    n_head: int = 4
    n_layer: int = 2
    dropout: float = 0.0

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


def causal_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Scaled dot-product attention with a strict decoder causal mask.

    Expected shape: (..., T, head_dim). Returns (output, normalized_weights).
    """
    if query.shape != key.shape or key.shape != value.shape:
        raise ValueError("query, key, and value must have matching shapes")
    if query.ndim < 2:
        raise ValueError("attention tensors need at least (time, channels)")
    time = query.shape[-2]
    scores = query @ key.transpose(-2, -1) / math.sqrt(query.shape[-1])
    future = torch.triu(
        torch.ones(time, time, dtype=torch.bool, device=query.device),
        diagonal=1,
    )
    scores = scores.masked_fill(future, float("-inf"))
    weights = F.softmax(scores, dim=-1)
    return weights @ value, weights


class CausalSelfAttention(nn.Module):
    def __init__(self, config: TinyConfig) -> None:
        super().__init__()
        if config.n_embd % config.n_head != 0:
            raise ValueError("n_embd must be divisible by n_head")
        self.n_head = config.n_head
        self.head_dim = config.n_embd // config.n_head
        self.qkv = nn.Linear(config.n_embd, 3 * config.n_embd, bias=False)
        self.proj = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, time, channels = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)

        def split_heads(t: torch.Tensor) -> torch.Tensor:
            return t.view(batch, time, self.n_head, self.head_dim).transpose(1, 2)

        q, k, v = map(split_heads, (q, k, v))
        out, weights = causal_attention(q, k, v)
        out = self.dropout(out)
        out = out.transpose(1, 2).contiguous().view(batch, time, channels)
        return self.proj(out)


class FeedForward(nn.Module):
    def __init__(self, config: TinyConfig) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd),
            nn.Dropout(config.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, config: TinyConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ff = FeedForward(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x


class TinyDecoderLM(nn.Module):
    def __init__(self, config: TinyConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)
        self.blocks = nn.Sequential(*(TransformerBlock(config) for _ in range(config.n_layer)))
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)

    def forward(
        self,
        idx: torch.Tensor,
        targets: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        batch, time = idx.shape
        if time > self.config.block_size:
            raise ValueError(
                f"sequence length {time} exceeds block_size {self.config.block_size}"
            )
        positions = torch.arange(time, device=idx.device)
        x = self.token_embedding(idx) + self.position_embedding(positions)
        x = self.blocks(x)
        logits = self.lm_head(self.ln_f(x))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss

    @torch.no_grad()
    def generate(
        self,
        idx: torch.Tensor,
        max_new_tokens: int,
        *,
        temperature: float = 1.0,
        top_k: int | None = 8,
        seed: int = 7,
    ) -> torch.Tensor:
        if temperature <= 0:
            raise ValueError("temperature must be > 0")
        generator = torch.Generator(device=idx.device)
        generator.manual_seed(seed)
        for _ in range(max_new_tokens):
            context = idx[:, -self.config.block_size :]
            logits, _ = self(context)
            logits = logits[:, -1, :] / temperature
            if top_k is not None:
                k = min(top_k, logits.shape[-1])
                cutoff = torch.topk(logits, k).values[:, [-1]]
                logits = logits.masked_fill(logits < cutoff, float("-inf"))
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1, generator=generator)
            idx = torch.cat((idx, next_token), dim=1)
        return idx


def sample_batch(
    token_ids: list[int],
    batch_size: int,
    block_size: int,
    *,
    generator: torch.Generator,
    device: str | torch.device = "cpu",
) -> tuple[torch.Tensor, torch.Tensor]:
    if len(token_ids) <= block_size:
        raise ValueError("corpus must contain more tokens than block_size")
    data = torch.tensor(token_ids, dtype=torch.long)
    starts = torch.randint(
        0,
        len(data) - block_size,
        (batch_size,),
        generator=generator,
    )
    x = torch.stack([data[i : i + block_size] for i in starts])
    y = torch.stack([data[i + 1 : i + block_size + 1] for i in starts])
    return x.to(device), y.to(device)


def train_steps(
    model: TinyDecoderLM,
    token_ids: list[int],
    *,
    steps: int = 80,
    batch_size: int = 16,
    learning_rate: float = 3e-3,
    seed: int = 7,
    device: str | torch.device = "cpu",
) -> list[float]:
    """Run a small, deterministic teaching loop and return per-step losses."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    model.to(device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    losses: list[float] = []

    for _ in range(steps):
        x, y = sample_batch(
            token_ids,
            batch_size,
            model.config.block_size,
            generator=generator,
            device=device,
        )
        _, loss = model(x, y)
        assert loss is not None
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
    return losses


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def future_attention_mass(weights: torch.Tensor) -> float:
    """Return the total probability mass assigned above the causal diagonal."""
    time = weights.shape[-1]
    future = torch.triu(
        torch.ones(time, time, dtype=torch.bool, device=weights.device),
        diagonal=1,
    )
    return float(weights.masked_select(future).sum().detach().cpu())
