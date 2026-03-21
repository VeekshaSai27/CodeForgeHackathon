import json
from skill_validation_service.services.gemini_service import generate_response


def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])


def generate_questions(skill):
    prompt = f"""
    Generate EXACTLY 8 practical questions to test {skill}.

    Rules:
    - Mix MCQ + scenario
    - Include difficulty: easy, medium, hard
    - Include correct answer
    - Include concept tag
    - Avoid theory
    - Output STRICT JSON

    Format:
    [
      {{
        "question": "...",
        "type": "mcq/scenario",
        "difficulty": "easy/medium/hard",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "concept": "..."
      }}
    ]
    """
    response = generate_response(prompt)
    return safe_json_parse(response)
