#!/usr/bin/env python3
PINNED="1.0.0"
cards=[
 {"name":"log-agent","version":PINNED,"skills":{"log_analysis"},"interfaces":{"text","structured"}},
 {"name":"log-lite","version":PINNED,"skills":{"log_analysis"},"interfaces":{"text"}},
 {"name":"travel-agent","version":PINNED,"skills":{"itinerary"},"interfaces":{"text"}},
]
required_skill="log_analysis"
required_interface="structured"
matches=[c["name"] for c in cards if c["version"]==PINNED and required_skill in c["skills"] and required_interface in c["interfaces"]]
print("matches:",matches)
for c in cards:
    print(f'  {c["name"]:12s} skills={sorted(c["skills"])} interfaces={sorted(c["interfaces"])}')
assert matches and all(required_skill in c["skills"] for c in cards if c["name"] in matches)
print("PASS: Agent Card-like discovery fixture matches capability and interface")
