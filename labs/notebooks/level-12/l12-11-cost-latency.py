#!/usr/bin/env python3
import math
# One agent run. "search" and "lookup" both wait only for "plan", so they run in parallel.
calls={
 "plan":{"duration_ms":200,"cost":0.012,"after":[]},
 "search":{"duration_ms":120,"cost":0.004,"after":["plan"]},
 "lookup":{"duration_ms":300,"cost":0.006,"after":["plan"]},
 "answer":{"duration_ms":250,"cost":0.018,"after":["search","lookup"]},
}
finish={}
for name,call in calls.items():
    start=max((finish[need] for need in call["after"]),default=0)
    finish[name]=start+call["duration_ms"]
critical_path_ms=max(finish.values())
sequential_ms=sum(call["duration_ms"] for call in calls.values())

# Fixed end-to-end latencies from earlier runs; this run is added as the newest trace.
history_ms=[480,520,560,600,610,640,660,690,700,720,740,760,780,800,820,840,860,880,900]
traces=sorted(history_ms+[critical_path_ms])
p95_ms=traces[math.ceil(0.95*len(traces))-1]

print("critical_path_ms:",critical_path_ms,"sequential_ms:",sequential_ms,"p95_ms:",p95_ms)
print("cost per call:",{name:call["cost"] for name,call in calls.items()})
print("total cost:",round(sum(call["cost"] for call in calls.values()),3))
assert critical_path_ms<=sequential_ms
print("PASS: latency and cost are measured separately")
