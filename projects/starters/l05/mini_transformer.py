"""Starter for p05-mini-transformer — Build a Mini Transformer.

Complete the TODO functions using only Python's standard library.
"""
import math

def dot(a, b):
    if len(a) != len(b):
        raise ValueError("dot-product vectors must match")
    return sum(x * y for x, y in zip(a, b))

def softmax(scores):
    # TODO: stable softmax (subtract max before exp).
    raise NotImplementedError

def layer_norm(vector, eps=1e-5):
    # TODO: normalize features of one token vector.
    raise NotImplementedError

def feed_forward(vector):
    # TODO: expand C -> 2C, apply a nonlinearity, then contract to C.
    raise NotImplementedError

def causal_multi_head_attention(sequence, n_head):
    """Return (output_sequence, weights).

    weights must be shaped conceptually as [head][query][key].
    Future key positions must keep weight 0.
    """
    # TODO: split channels into heads, compute scaled causal attention,
    # mix values, and concatenate heads back to the original width.
    raise NotImplementedError

def residual_add(sequence, update):
    # TODO: elementwise addition with explicit shape checks.
    raise NotImplementedError

def transformer_block(sequence, n_head):
    # TODO: pre-norm attention residual, then pre-norm feed-forward residual.
    raise NotImplementedError

def stack_blocks(sequence, n_head, depth):
    # TODO: repeat the block while preserving sequence/feature shape.
    raise NotImplementedError

def embed_token(token_id, position, width):
    # Deterministic teaching embedding; keep this function unchanged.
    token = [(((token_id + 1) * (j + 3)) % 17) / 17.0 for j in range(width)]
    pos = [(((position + 1) * (j + 5)) % 19) / 19.0 for j in range(width)]
    return [a + b for a, b in zip(token, pos)]

def mini_transformer(token_ids, vocab_size=23, context=8, width=8, n_head=2, depth=2):
    # TODO: embeddings -> stacked blocks -> final norm -> vocabulary logits.
    raise NotImplementedError
