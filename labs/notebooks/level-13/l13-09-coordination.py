#!/usr/bin/env python3
deps={
 "log_a":set(),"log_b":set(),"policy":{"log_a","log_b"},"report":{"policy"}
}
done=set(); waves=[]
while len(done)<len(deps):
    ready=sorted(k for k,v in deps.items() if k not in done and v<=done)
    if not ready: raise RuntimeError("cycle")
    waves.append(ready); done.update(ready)
print("waves:",waves)
pattern="parallel waves under a supervisor" if any(len(w)>1 for w in waves) else "pipeline (one step at a time)"
print("schedule:",pattern)
position={k:i for i,w in enumerate(waves) for k in w}
assert all(position[d]<position[k] for k,v in deps.items() for d in v)
assert waves[-1]==["report"]
print("PASS: coordination follows dependency structure")
