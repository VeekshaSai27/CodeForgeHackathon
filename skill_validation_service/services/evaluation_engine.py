def evaluate(questions, answers):
    weights = {"easy": 0.2, "medium": 0.3, "hard": 0.5}

    score = 0
    concept_errors = {}
    correctness = []

    for q, ans in zip(questions, answers):
        is_correct = ans == q["answer"]
        correctness.append(1 if is_correct else 0)

        if is_correct:
            score += weights[q["difficulty"]]
        else:
            concept = q["concept"]
            concept_errors[concept] = concept_errors.get(concept, 0) + 1

    proficiency = min(score, 1.0)

    return proficiency, concept_errors, correctness