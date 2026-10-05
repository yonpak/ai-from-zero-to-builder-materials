#!/usr/bin/env python3
"""L14.9 local preflight: compare deployments by immutable identity, not by tag."""
IDENTITY_FIELDS = ("image_digest", "model_revision", "runtime_version", "config_hash")

running = {"tag": "serve:1.2", "image_digest": "sha256:aaa", "model_revision": "model-r7",
           "runtime_version": "runtime-r3", "config_hash": "cfg-1"}
candidate = {"tag": "serve:1.2", "image_digest": "sha256:aaa", "model_revision": "model-r7",
             "runtime_version": "runtime-r3", "config_hash": "cfg-1"}


def identity(d):
    return tuple(d[f] for f in IDENTITY_FIELDS)


print("running identity:  ", identity(running))
print("candidate identity:", identity(candidate))
print("tag comparison:     ", "same" if running["tag"] == candidate["tag"] else "changed")
print("identity comparison:", "same" if identity(running) == identity(candidate) else "changed")
changed = [f for f in IDENTITY_FIELDS if running[f] != candidate[f]]
print("changed identity fields:", changed)

same_tag_new_digest = {**running, "image_digest": "sha256:bbb"}
new_tag_same_identity = {**running, "tag": "serve:latest"}
assert same_tag_new_digest["tag"] == running["tag"]
assert identity(same_tag_new_digest) != identity(running)
assert new_tag_same_identity["tag"] != running["tag"]
assert identity(new_tag_same_identity) == identity(running)

print("PASS: immutable identity detects deployment changes that mutable tags can hide")
