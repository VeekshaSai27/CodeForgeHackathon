import json
import re
from skill_validation_service.services.gemini_service import generate_response


def _safe_json_parse(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
        return json.loads(cleaned)


_PROMPT = """
Generate a skill assessment quiz for the following skills: {skills_list}

For EACH skill generate EXACTLY 8 questions:
- 3 easy MCQ questions
- 3 medium MCQ questions  
- 2 medium coding questions

Rules:
- MCQ: type="mcq", options array with 4 choices, answer = correct option text (full text, not a letter)
- Coding: type="coding", starterCode snippet, language must match the skill ("python" for Python/ML/data/NumPy/Pandas/TensorFlow/PyTorch/Matplotlib/OpenCV/Flask/Django skills, "javascript" for web/JS/React/Node skills), answer=""
- Every question must have: question, type, difficulty, options, answer, concept, skill fields
- Output STRICT JSON only, no markdown, no explanation

Output format:
{{
  "SkillName": [
    {{"skill":"SkillName","question":"...","type":"mcq","difficulty":"easy","options":["A","B","C","D"],"answer":"A","concept":"...","starterCode":"","language":""}},
    ...8 questions...
  ],
  ...one key per skill...
}}
"""


def generate_questions_batch(skills: list[str]) -> dict[str, list]:
    """Generate questions for all skills in a single Gemini call."""
    if not skills:
        return {}

    prompt = _PROMPT.format(skills_list=", ".join(skills))
    raw = generate_response(prompt)
    if not raw:
        return {skill: [] for skill in skills}

    try:
        data = _safe_json_parse(raw)
        result = {}
        for skill in skills:
            # Try exact match first, then case-insensitive
            qs = data.get(skill) or next(
                (v for k, v in data.items() if k.lower() == skill.lower()), []
            )
            result[skill] = qs if isinstance(qs, list) else []
        return result
    except Exception as e:
        print(f"❌ Batch question parse failed: {e}")
        return {skill: [] for skill in skills}


def generate_questions(skill: str) -> list:
    """Single-skill wrapper — used when called individually."""
    return generate_questions_batch([skill]).get(skill, [])
