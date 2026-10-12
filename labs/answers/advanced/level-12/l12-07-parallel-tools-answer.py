#!/usr/bin/env python3
"""Reference answer for L12.07."""


def dependency_waves(deps):
    done = set()
    waves = []
    while len(done) < len(deps):
        ready = sorted(name for name, needs in deps.items() if name not in done and needs <= done)
        if not ready:
            raise RuntimeError("dependency cycle or unsatisfied dependency")
        waves.append(ready)
        done.update(ready)
    return waves


deps = {
    "user_profile": set(),
    "inventory_lookup": set(),
    "recommendation": {"user_profile", "inventory_lookup"},
    "write_report": {"recommendation"},
}
assert dependency_waves(deps) == [["inventory_lookup", "user_profile"], ["recommendation"], ["write_report"]]
assert dependency_waves({"a": set(), "b": {"a"}}) == [["a"], ["b"]]
try:
    dependency_waves({"a": {"b"}, "b": {"a"}})
except RuntimeError:
    pass
else:
    raise AssertionError("cycle must be rejected")
print("PASS: L12.07 reference answer exposes ready waves and rejects cycles")
