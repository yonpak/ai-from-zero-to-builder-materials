#!/usr/bin/env python3
deps={
 "user_profile":set(),
 "inventory_lookup":set(),
 "recommendation":{"user_profile","inventory_lookup"},
 "write_report":{"recommendation"},
}
done=set(); waves=[]
while len(done)<len(deps):
    ready=sorted(name for name,needs in deps.items() if name not in done and needs<=done)
    if not ready: raise RuntimeError("cycle")
    waves.append(ready); done.update(ready)
print("waves:",waves)
print("wave count:",len(waves))
# Invariant for any dependency graph: a task runs only after every task it depends on.
wave_of={name:number for number,wave in enumerate(waves) for name in wave}
assert all(wave_of[need]<wave_of[name] for name,needs in deps.items() for need in needs)
print("PASS: every task runs after its dependencies")
