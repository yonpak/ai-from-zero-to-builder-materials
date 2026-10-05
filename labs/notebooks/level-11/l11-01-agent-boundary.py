systems = [
    {"name": "single-call", "steps": 1, "next_action_depends_on_observation": False},
    {"name": "fixed-workflow", "steps": 3, "next_action_depends_on_observation": False},
    {"name": "agent-like-loop", "steps": 3, "next_action_depends_on_observation": True},
]

for system in systems:
    kind = "agent-like" if system["next_action_depends_on_observation"] else "fixed"
    print(system["name"], "=>", kind, system)
