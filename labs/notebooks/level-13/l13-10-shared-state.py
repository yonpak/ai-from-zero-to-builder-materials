#!/usr/bin/env python3
"""L13.10 local preflight: expected-version writes reject stale updates to shared state."""
SECOND_WRITER_RELOADS = False  # try True: writer B reads the latest version before writing

state = {"version": 7, "status": "working", "evidence": []}


def write(writer, expected_version, patch):
    global state
    if expected_version != state["version"]:
        print(f"{writer}: expected v{expected_version}, store is v{state['version']} -> REJECTED (stale)")
        return False
    state = {**state, **patch, "version": state["version"] + 1}
    print(f"{writer}: expected v{expected_version} -> written, store is now v{state['version']}")
    return True


seen_by_a = seen_by_b = state["version"]  # both writers read the same version
a_written = write("A", seen_by_a, {"status": "review"})
version_after_a = state["version"]
assert a_written is True
assert version_after_a == seen_by_a + 1

if SECOND_WRITER_RELOADS:
    seen_by_b = state["version"]
    print(f"B reloads and now sees v{seen_by_b} with status {state['status']!r}")

b_written = write("B", seen_by_b, {"status": "completed"})
print("final:", state)

if SECOND_WRITER_RELOADS:
    assert b_written is True
    assert state["version"] == version_after_a + 1
    assert state["status"] == "completed"
else:
    assert b_written is False
    assert state["version"] == version_after_a
    assert state["status"] == "review"

print("PASS: stale writes leave state unchanged; refreshed writes advance exactly one version")
