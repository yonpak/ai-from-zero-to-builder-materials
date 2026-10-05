#!/usr/bin/env python3
import math

arrival_rps = 22
safe_rps_per_replica = 8
target_utilization = 0.8  # try 0.98

required = math.ceil(arrival_rps / (safe_rps_per_replica * target_utilization))
planned = required + 1  # N+1: survive the loss of one replica
after_failure = planned - 1
utilization_after_failure = arrival_rps / (after_failure * safe_rps_per_replica)
spare_rps = after_failure * safe_rps_per_replica - arrival_rps
risk = "high" if utilization_after_failure > 0.85 else "low"
print({"target_utilization": target_utilization, "required_replicas": required, "planned_replicas": planned})
print({"replicas_after_one_failure": after_failure,
       "utilization_after_failure": round(utilization_after_failure, 2),
       "spare_rps_after_failure": spare_rps, "queue_risk": risk})
assert after_failure >= required
print("PASS: capacity plan includes one-replica failure reserve")
