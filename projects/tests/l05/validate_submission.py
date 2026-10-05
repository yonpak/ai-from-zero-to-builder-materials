import importlib.util
import math
import pathlib
import sys

def load_module(path):
    spec = importlib.util.spec_from_file_location("submission", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load submission")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def close(a, b, tol=1e-7):
    return abs(a - b) <= tol

def validate(path):
    m = load_module(path)
    required = [
        "softmax","layer_norm","feed_forward","causal_multi_head_attention",
        "residual_add","transformer_block","stack_blocks","mini_transformer"
    ]
    for name in required:
        if not callable(getattr(m, name, None)):
            raise AssertionError(f"missing callable: {name}")

    probs = m.softmax([0.0, 2.0, 1.0])
    assert len(probs) == 3 and close(sum(probs), 1.0)
    assert probs[1] == max(probs)

    norm = m.layer_norm([101.0, 102.0, 103.0])
    assert len(norm) == 3 and abs(sum(norm) / 3) < 1e-6

    seq = [
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8],
        [0.2,0.1,0.4,0.3,0.6,0.5,0.8,0.7],
        [0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.3,0.5,0.7,0.9,0.2,0.4,0.6,0.8],
    ]
    out, weights = m.causal_multi_head_attention(seq, 2)
    assert len(out) == len(seq)
    assert all(len(row) == 8 for row in out)
    assert len(weights) == 2
    for head in weights:
        for q, row in enumerate(head):
            assert len(row) == len(seq)
            assert abs(sum(row) - 1.0) < 1e-6
            assert sum(abs(v) for v in row[q+1:]) == 0.0

    try:
        m.causal_multi_head_attention([row[:6] for row in seq], 4)
        raise AssertionError("head divisibility error was not raised")
    except ValueError:
        pass

    block, _ = m.transformer_block(seq, 2)
    assert len(block) == len(seq) and all(len(row) == 8 for row in block)

    stacked, _ = m.stack_blocks(seq, 2, 3)
    assert len(stacked) == len(seq) and all(len(row) == 8 for row in stacked)

    ids_a = [1,2,3,4,5]
    ids_b = [1,2,3,9,10]
    logits_a, all_weights = m.mini_transformer(ids_a, vocab_size=23, context=8, width=8, n_head=2, depth=2)
    logits_b, _ = m.mini_transformer(ids_b, vocab_size=23, context=8, width=8, n_head=2, depth=2)
    assert len(logits_a) == 5 and all(len(row) == 23 for row in logits_a)
    for t in range(3):
        assert all(abs(a-b) < 1e-7 for a,b in zip(logits_a[t], logits_b[t])), "future token changed earlier logits"

    future_mass = 0.0
    for block_weights in all_weights:
        for head in block_weights:
            for q, row in enumerate(head):
                future_mass += sum(abs(v) for v in row[q+1:])
    assert future_mass == 0.0

    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_submission.py PATH")
    validate(pathlib.Path(sys.argv[1]))
    print("PASS: p05-mini-transformer objective checks")
