def run(actions, max_steps=4, repeat_limit=3):
    seen = {}
    for step, action in enumerate(actions[:max_steps], start=1):
        seen[action] = seen.get(action, 0) + 1
        print("step", step, "action", action)
        if action == "finish":
            return "success"
        if seen[action] >= repeat_limit:
            return "repeated_action"
    return "max_steps"


print("success case:", run(["get_order", "check_policy", "finish"]))
print("repeat case:", run(["search_order", "search_order", "search_order", "search_order"]))
