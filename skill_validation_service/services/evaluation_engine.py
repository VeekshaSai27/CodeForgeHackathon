def evaluate(questions, answers):
    weights = {"easy": 0.2, "medium": 0.3, "hard": 0.5}

    score = 0
    concept_errors = {}
    correctness = []

    for q, ans in zip(questions, answers):
        q_type = q.get("type", "mcq")
        if q_type == "coding":
            # Coding: any non-empty submission counts as attempted (medium weight)
            is_correct = bool(ans and ans.strip())
        else:
            is_correct = ans == q["answer"]
        correctness.append(1 if is_correct else 0)

        if is_correct:
            score += weights.get(q.get("difficulty", "medium"), 0.3)
        else:
            concept = q.get("concept", "unknown")
            concept_errors[concept] = concept_errors.get(concept, 0) + 1

    proficiency = min(score, 1.0)

    return proficiency, concept_errors, correctness