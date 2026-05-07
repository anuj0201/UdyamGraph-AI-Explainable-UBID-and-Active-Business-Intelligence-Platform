def decide(score: float):
    if score > 0.85:
        return "auto_merge"
    elif score > 0.65:
        return "review"
    else:
        return "reject"