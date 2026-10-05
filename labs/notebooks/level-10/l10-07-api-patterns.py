#!/usr/bin/env python3
recorded_items = ["inc-1", "inc-2", "inc-3"]

def fetch_page(page, page_size):
    start = page * page_size
    items = recorded_items[start:start + page_size]
    return {"items": items, "complete": start + page_size >= len(recorded_items)}

for page_size in [2, 1]:
    first = fetch_page(0, page_size)
    print("page_size", page_size, "->", first)

assert fetch_page(0, 2)["complete"] is False
assert fetch_page(1, 2)["complete"] is True
