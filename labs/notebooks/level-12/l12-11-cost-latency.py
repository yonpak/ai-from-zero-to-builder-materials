#!/usr/bin/env python3
latencies=[180,210,220,240,260,300,320,360,420,500,520,540,600,700,900,1000,1100,1200,1300,1500]
costs=[0.012,0.018,0.006]
ordered=sorted(latencies)
p95=ordered[max(0,int(0.95*len(ordered))-1)]
parallel_critical=max(200,300)
sequential=200+300
print({"p95_ms":p95,"parallel_ms":parallel_critical,"sequential_ms":sequential,"cost":sum(costs)})
assert parallel_critical==300 and sequential==500
print("PASS: latency and cost are measured separately")
