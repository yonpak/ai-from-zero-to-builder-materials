#!/usr/bin/env python3
"""L14.7 preflight: serving load and inference budget change different operational metrics."""
import math
CONCURRENCY = 4          # requests the server runs at the same time; try 8
GPU_COST_PER_S = 0.002   # cost units per second of GPU time
REASONING_BUDGET = 1     # illustrative inference-work units; try 3
output_tokens = [120, 150, 200, 160, 90, 180, 140, 210]


def p95(values):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def summarize(concurrency, tokens, gpu_cost_per_s):
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    if not tokens or sum(tokens) <= 0:
        raise ValueError("token workload must contain positive work")

    per_token_ms = 8 * (1 + 0.15 * (concurrency - 1))
    traces = []
    for i, token_count in enumerate(tokens):
        ttft = 150 + 30 * (concurrency - 1) + (i % 4) * 20
        traces.append({
            "ttft_ms": ttft,
            "e2e_ms": round(ttft + token_count * per_token_ms),
            "tokens": token_count,
        })

    waves = [traces[i:i + concurrency] for i in range(0, len(traces), concurrency)]
    wall_s = sum(max(t["e2e_ms"] for t in wave) for wave in waves) / 1000
    total_tokens = sum(tokens)
    metrics = {
        "p95_ttft_ms": p95(t["ttft_ms"] for t in traces),
        "p95_e2e_ms": p95(t["e2e_ms"] for t in traces),
        "tokens_per_second": round(total_tokens / wall_s, 1),
        "cost_per_1k_tokens": round(gpu_cost_per_s * wall_s / total_tokens * 1000, 4),
    }
    assert metrics["p95_e2e_ms"] >= metrics["p95_ttft_ms"] > 0
    assert metrics["tokens_per_second"] > 0
    assert metrics["cost_per_1k_tokens"] >= 0
    return metrics


def reasoning_profile(budget):
    """Illustrative only: make the budget/quality/latency tradeoff visible."""
    if budget < 1:
        raise ValueError("reasoning budget must be at least 1")
    return {
        "simulation_only": True,
        "inference_budget": budget,
        "hard_cases_solved": min(5, 2 + budget),
        "end_to_end_ms": 700 + 350 * budget,
        "compute_units": round(1.5 * budget, 1),
    }


metrics = summarize(CONCURRENCY, output_tokens, GPU_COST_PER_S)
print("concurrency:", CONCURRENCY)
print(metrics)
print("reasoning_profile:", reasoning_profile(REASONING_BUDGET))

regression_tokens = [100, 100, 100, 100]
serial = summarize(1, regression_tokens, 0.002)
parallel = summarize(4, regression_tokens, 0.002)
assert parallel["p95_ttft_ms"] > serial["p95_ttft_ms"]
assert parallel["tokens_per_second"] > serial["tokens_per_second"]
assert parallel["cost_per_1k_tokens"] != serial["cost_per_1k_tokens"]

small_budget = reasoning_profile(1)
large_budget = reasoning_profile(3)
assert large_budget["hard_cases_solved"] >= small_budget["hard_cases_solved"]
assert large_budget["end_to_end_ms"] > small_budget["end_to_end_ms"]
assert large_budget["compute_units"] > small_budget["compute_units"]

print("PASS: serving load and inference budget expose separate tradeoffs")
