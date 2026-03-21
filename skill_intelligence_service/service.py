import json
import re

from dotenv import load_dotenv

load_dotenv()

from .models import SkillDNA
from .prompts import SKILL_EXTRACTION_PROMPT
from shared.gemini_pool import generate_with_retry


def build_skill_dna(resume: str, jd: str) -> SkillDNA:
    prompt = SKILL_EXTRACTION_PROMPT.format(
        resume=resume.strip() or "Not provided.",
        jd=jd.strip() or "Not provided.",
    )
    raw = generate_with_retry(prompt, temperature=0.2)
    return _parse_and_validate(raw)


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
