import json
import re

import networkx as nx
from dotenv import load_dotenv

from shared.gemini_pool import generate_with_retry

load_dotenv()

_REASONING_PROMPT = """
You are an AI learning advisor explaining why certain skills are prioritized for a learner.

You are given a list of skills with their pre-computed scores and attributes.
Your ONLY job is to write a short, clear, human-readable reason (1-2 sentences) for each skill.

Rules:
- Do NOT change or suggest scores
- Do NOT reorder skills
- Base your reasoning on the provided attributes (importance, proficiency, confidence, score, prerequisites)
- Be specific — mention actual values where helpful
- Keep each reason under 25 words

Skills data:
{skills_data}

Return ONLY valid JSON in this exact format:
{{
  "reasoning": {{
    "Skill Name": "Reason why this skill is prioritized.",
    ...
  }}
}}
"""


def generate_reasoning(
    G: nx.DiGraph,
    scores: dict[str, float],
    valid_skills: list[str],
) -> dict[str, str]:
    skills_data = _build_skills_data(G, scores, valid_skills)
    prompt = _REASONING_PROMPT.format(skills_data=json.dumps(skills_data, indent=2))

    try:
        raw = generate_with_retry(prompt, temperature=0.3)
        return _parse_reasoning(raw, valid_skills)
    except Exception as e:
        print(f"⚠️ Reasoning generation failed: {e}. Using fallback reasoning.")
        return _fallback_reasoning(G, scores, valid_skills)


def _build_skills_data(
    G: nx.DiGraph,
    scores: dict[str, float],
    valid_skills: list[str],
) -> list[dict]:
    return [
        {
            "skill": skill,
            "score": scores[skill],
            "importance": G.nodes[skill].get("importance", 0.5),
            "proficiency": G.nodes[skill].get("proficiency", 0.0),
            "confidence": G.nodes[skill].get("confidence", 0.0),
            "prerequisites": list(G.predecessors(skill)),
        }
        for skill in sorted(valid_skills, key=lambda s: scores[s], reverse=True)
    ]


def _parse_reasoning(raw: str, valid_skills: list[str]) -> dict[str, str]:
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    data = json.loads(cleaned)
    reasoning = data.get("reasoning", {})
    for skill in valid_skills:
        if skill not in reasoning:
            reasoning[skill] = f"{skill} is unlocked and has a notable learning gap."
    return reasoning


def _fallback_reasoning(
    G: nx.DiGraph,
    scores: dict[str, float],
    valid_skills: list[str],
) -> dict[str, str]:
    reasoning = {}
    for skill in valid_skills:
        importance = G.nodes[skill].get("importance", 0.5)
        proficiency = G.nodes[skill].get("proficiency", 0.0)
        score = scores[skill]
        reasoning[skill] = (
            f"{skill} has a pressure score of {score:.2f} "
            f"(importance: {importance:.2f}, proficiency: {proficiency:.2f})."
        )
    return reasoning
