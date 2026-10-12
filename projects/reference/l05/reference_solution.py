"""Reference implementation for p05-mini-transformer.

This is a deterministic CPU teaching model. It uses identity Q/K/V projections so
the project can focus on attention/block semantics without a training dependency.
"""
import math

def dot(a, b):
    if len(a) != len(b):
        raise ValueError("dot-product vectors must match")
    return sum(x * y for x, y in zip(a, b))

def softmax(scores):
    if not scores:
        raise ValueError("softmax needs at least one score")
    m = max(scores)
    exp = [math.exp(v - m) for v in scores]
    total = sum(exp)
    return [v / total for v in exp]

def layer_norm(vector, eps=1e-5):
    if not vector:
        raise ValueError("layer_norm needs features")
    mean = sum(vector) / len(vector)
    variance = sum((x - mean) ** 2 for x in vector) / len(vector)
    denom = math.sqrt(variance + eps)
    return [(x - mean) / denom for x in vector]

def feed_forward(vector):
    # Expand C -> 2C, apply ReLU, then contract to C.
    hidden = []
    for value in vector:
        hidden.extend([max(0.0, value), max(0.0, -value)])
    return [hidden[2*i] - hidden[2*i + 1] for i in range(len(vector))]

def _split_vector(vector, n_head):
    width = len(vector)
    if n_head <= 0 or width % n_head != 0:
        raise ValueError("embedding width must be divisible by n_head")
    d = width // n_head
    return [vector[h*d:(h+1)*d] for h in range(n_head)]

def causal_multi_head_attention(sequence, n_head):
    if not sequence:
        raise ValueError("sequence cannot be empty")
    width = len(sequence[0])
    if any(len(row) != width for row in sequence):
        raise ValueError("all token vectors must have the same width")
    if n_head <= 0 or width % n_head != 0:
        raise ValueError("embedding width must be divisible by n_head")

    split = [_split_vector(row, n_head) for row in sequence]
    head_dim = width // n_head
    scale = math.sqrt(head_dim)
    all_head_outputs = [[None for _ in sequence] for _ in range(n_head)]
    all_weights = [[[0.0 for _ in sequence] for _ in sequence] for _ in range(n_head)]

    for h in range(n_head):
        for q_index, token_heads in enumerate(split):
            query = token_heads[h]
            legal_keys = [split[k_index][h] for k_index in range(q_index + 1)]
            scores = [dot(query, key) / scale for key in legal_keys]
            weights = softmax(scores)
            for k_index, weight in enumerate(weights):
                all_weights[h][q_index][k_index] = weight
            out = []
            for j in range(head_dim):
                out.append(sum(weight * split[k][h][j] for k, weight in enumerate(weights)))
            all_head_outputs[h][q_index] = out

    merged = []
    for t in range(len(sequence)):
        row = []
        for h in range(n_head):
            row.extend(all_head_outputs[h][t])
        merged.append(row)
    return merged, all_weights

def residual_add(sequence, update):
    if len(sequence) != len(update):
        raise ValueError("residual sequence lengths must match")
    out = []
    for left, right in zip(sequence, update):
        if len(left) != len(right):
            raise ValueError("residual feature widths must match")
        out.append([a + b for a, b in zip(left, right)])
    return out

def transformer_block(sequence, n_head):
    norm1 = [layer_norm(row) for row in sequence]
    attn, weights = causal_multi_head_attention(norm1, n_head)
    x1 = residual_add(sequence, attn)
    norm2 = [layer_norm(row) for row in x1]
    ff = [feed_forward(row) for row in norm2]
    return residual_add(x1, ff), weights

def stack_blocks(sequence, n_head, depth):
    if depth <= 0:
        raise ValueError("depth must be positive")
    x = [list(row) for row in sequence]
    weights = []
    for _ in range(depth):
        x, block_weights = transformer_block(x, n_head)
        weights.append(block_weights)
    return x, weights

def embed_token(token_id, position, width):
    if token_id < 0 or position < 0 or width <= 0:
        raise ValueError("token_id/position must be non-negative and width positive")
    token = [(((token_id + 1) * (j + 3)) % 17) / 17.0 for j in range(width)]
    pos = [(((position + 1) * (j + 5)) % 19) / 19.0 for j in range(width)]
    return [a + b for a, b in zip(token, pos)]

def mini_transformer(token_ids, vocab_size=23, context=8, width=8, n_head=2, depth=2):
    if not token_ids:
        raise ValueError("token_ids cannot be empty")
    if len(token_ids) > context:
        raise ValueError("sequence exceeds context")
    if any(t < 0 or t >= vocab_size for t in token_ids):
        raise ValueError("token id outside vocabulary")
    if width % n_head != 0:
        raise ValueError("embedding width must be divisible by n_head")

    x = [embed_token(token_id, pos, width) for pos, token_id in enumerate(token_ids)]
    x, weights = stack_blocks(x, n_head, depth)
    x = [layer_norm(row) for row in x]

    # Deterministic vocabulary projection: dot each state with a token-only basis.
    basis = [embed_token(v, 0, width) for v in range(vocab_size)]
    logits = [[dot(row, b) for b in basis] for row in x]
    return logits, weights

if __name__ == "__main__":
    ids = [1, 2, 3, 4, 5]
    logits, weights = mini_transformer(ids)
    print("logits shape:", (len(logits), len(logits[0])))
    future_mass = 0.0
    for block in weights:
        for head in block:
            for q, row in enumerate(head):
                future_mass += sum(row[q+1:])
    print("future attention mass:", future_mass)
