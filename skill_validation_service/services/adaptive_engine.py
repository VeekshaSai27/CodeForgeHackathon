def get_next_difficulty(history):
    if not history:
        return "medium"

    score = sum(history) / len(history)

    if score > 0.75:
        return "hard"
    elif score < 0.4:
        return "easy"
    else:
        return "medium"