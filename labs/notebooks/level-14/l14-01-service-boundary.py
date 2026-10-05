#!/usr/bin/env python3
"""L14.1 local Lab: liveness, readiness, and deployment identity are separate facts."""
state = {"process_alive": True, "model_loaded": True, "dependencies_ready": True}
liveness = state["process_alive"]
readiness = all(state.values())
deployment = {"service_version": "1.2.0", "model_revision": "model-r7", "runtime": "serving-r3", "config_hash": "cfg-a1"}
print({"liveness": liveness, "readiness": readiness})
print("deployment:", deployment)
print("restart the process?", "no" if liveness else "yes")
print("send user traffic?", "yes" if readiness else "no (keep out of the load balancer until ready)")
assert liveness
print("PASS: service lifecycle separates liveness, readiness, and deployment identity")
