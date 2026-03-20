import json
import os
import re

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

from .models import SkillDNA
from .prompts import SKILL_EXTRACTION_PROMPT

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    generation_config=genai.GenerationConfig(
        temperature=0.2,
        response_mime_type="application/json",
    ),
)


def build_skill_dna(resume: str, jd: str) -> SkillDNA:
    """
    Extract, normalize, and score skills from a resume and job description.

    Args:
        resume: Raw resume text (can be empty or vague).
        jd:     Raw job description text (can be empty or vague).

    Returns:
        Validated SkillDNA profile.
    """
    prompt = SKILL_EXTRACTION_PROMPT.format(
        resume=resume.strip() or "Not provided.",
        jd=jd.strip() or "Not provided.",
    )
    response = _model.generate_content(prompt)
    return _parse_and_validate(response.text)


def _parse_and_validate(raw: str) -> SkillDNA:
    """Parse Gemini JSON output and validate against SkillDNA schema."""
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    parsed = json.loads(cleaned)
    skill_dna = SkillDNA(**parsed)

    skill_set = set(skill_dna.skills)
    for field_name, field_dict in [("importance", skill_dna.importance), ("confidence", skill_dna.confidence)]:
        unknown = set(field_dict.keys()) - skill_set
        if unknown:
            raise ValueError(f"'{field_name}' contains skills not in skills list: {unknown}")

    for skill in skill_dna.skills:
        skill_dna.importance.setdefault(skill, 0.5)
        skill_dna.confidence.setdefault(skill, 0.0)

    return skill_dna
