#!/usr/bin/env python3
"""Learner exercise for L12.07: schedule independent tool work in waves."""

DEPS = {
    "user_profile": set(),
    "inventory_lookup": set(),
    "recommendation": {"user_profile", "inventory_lookup"},
    "write_report": {"recommendation"},
}


def dependency_waves(deps):
    # TODO 1: collect all not-yet-done tasks whose dependencies are satisfied.
    # TODO 2: advance a whole ready wave at once.
    # TODO 3: raise RuntimeError when no task is ready before completion.
    raise NotImplementedError("TODO: implement dependency-wave scheduling")


waves = dependency_waves(DEPS)
assert waves[0] == ["inventory_lookup", "user_profile"]
assert waves[-1] == ["write_report"]
print("PASS: learner scheduler exposes safe parallel waves")
