records = [
    {"id": "m1", "category": "preference", "scope": "user-7", "source": "profile", "age_days": 2, "sensitive": False},
    {"id": "m2", "category": "preference", "scope": "user-7", "source": "model_guess", "age_days": 1, "sensitive": False},
    {"id": "m3", "category": "account_secret", "scope": "user-7", "source": "tool", "age_days": 1, "sensitive": True},
    {"id": "m4", "category": "preference", "scope": "user-8", "source": "profile", "age_days": 2, "sensitive": False},
]

def allowed(record):
    return (
        record["category"] == "preference"
        and record["source"] == "profile"
        and not record["sensitive"]
        and record["age_days"] <= 30
    )

retrieved = [r for r in records if r["scope"] == "user-7" and allowed(r)]
print("approved persistent records:", [r["id"] for r in records if allowed(r)])
print("retrieved for user-7:", [r["id"] for r in retrieved])
