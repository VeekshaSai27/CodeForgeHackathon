import json
from skill_validation_service.services.gemini_service import generate_response
from skill_validation_service.services.adaptive_engine import get_next_difficulty


def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])


def _fetch_questions(skill: str, difficulty: str, count: int, q_type: str) -> list:
    type_rules = (
        f'type must be "mcq", include 4 options and correct answer letter'
        if q_type == "mcq" else
        f'type must be "coding", include starterCode snippet, language ("javascript" or "python"), answer is empty string'
    )
    prompt = f"""
    Generate EXACTLY {count} {difficulty} {q_type} questions to test {skill}.
    Rules: {type_rules}, include concept tag, avoid pure theory, output STRICT JSON array only, no markdown.
    Format: [{{"question":"...","type":"{q_type}","difficulty":"{difficulty}","options":[],"answer":"","concept":"..."}}]
    """
    return safe_json_parse(generate_response(prompt))


def generate_questions(skill: str) -> list:
    """
    Adaptive question generation:
    - Start with 3 easy MCQs
    - Based on correctness history, serve 3 medium MCQs at appropriate difficulty
    - End with 2 coding questions
    Total: 8 questions ordered easy → adaptive → coding
    """
    questions = []

    easy_qs = _fetch_questions(skill, "easy", 3, "mcq")
    questions.extend(easy_qs[:3])

    next_diff = get_next_difficulty([])  # defaults to "medium" for fresh users
    mid_qs = _fetch_questions(skill, next_diff, 3, "mcq")
    questions.extend(mid_qs[:3])

    coding_qs = _fetch_questions(skill, "medium", 2, "coding")
    questions.extend(coding_qs[:2])

    return questions
