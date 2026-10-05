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
assert waves[0]==["inventory_lookup","user_profile"]
assert waves[-1]==["write_report"]
print("PASS: dependency waves expose safe parallel work")
