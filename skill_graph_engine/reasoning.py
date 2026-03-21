import json
import re

import networkx as nx
from dotenv import load_dotenv

from shared.gemini_pool import generate_with_retry

load_dotenv()

_DEFAULTS = {"alpha": 0.4, "beta": 0.3, "gamma": 0.2, "delta": 0.1}

_WEIGHTS_PROMPT = """
You are calibrating a skill prioritization algorithm for a personalized learning platform.

The scoring formula is:
  Score = alpha * Importance + beta * (1 - Proficiency) + gamma * DependencyCentrality - delta * Confidence

User profile summary:
- Total skills: {num_skills}
- Average importance: {avg_importance:.2f}
- Average proficiency: {avg_proficiency:.2f}
- Average confidence: {avg_confidence:.2f}
- Learner level: {level}
- Profile type: {profile_type}

Rules:
- alpha + beta + gamma + delta MUST equal exactly 1.0
- All values must be between 0.05 and 0.6
- Higher beta if learner has large skill gaps (low proficiency)
- Higher alpha if job role demands specific high-importance skills
- Higher gamma if skills have many interdependencies
- Lower delta if learner is overconfident (confidence >> proficiency)

Return ONLY valid JSON:
{{"alpha": 0.0, "beta": 0.0, "gamma": 0.0, "delta": 0.0}}
"""


def infer_weights(
    importance: dict[str, float],
    confidence: dict[str, float],
    proficiency: dict[str, float],
) -> dict[str, float]:
    """
    Ask Gemini to infer scoring weights based on the user's skill profile.
    Falls back to defaults if inference fails or returns invalid weights.
    """
    if not importance:
        return _DEFAULTS.copy()

    skills = list(importance.keys())
    avg_importance  = sum(importance.values()) / len(importance)
    avg_proficiency = sum(proficiency.get(s, 0.0) for s in skills) / len(skills)
    avg_confidence  = sum(confidence.get(s, 0.0) for s in skills) / len(skills)

    level = (
        "beginner"     if avg_proficiency < 0.3 else
        "intermediate" if avg_proficiency < 0.65 else
        "advanced"
    )
    importance_variance = max(importance.values()) - min(importance.values())
    profile_type = "specialist (high-variance JD)" if importance_variance > 0.4 else "generalist (broad JD)"

    prompt = _WEIGHTS_PROMPT.format(
        num_skills=len(skills),
        avg_importance=avg_importance,
        avg_proficiency=avg_proficiency,
        avg_confidence=avg_confidence,
        level=level,
        profile_type=profile_type,
    )

    try:
        raw = generate_with_retry(prompt, temperature=0.1)
        return _parse_weights(raw)
    except Exception as e:
        print(f"⚠️ Weight inference failed: {e}. Using defaults.")
        return _DEFAULTS.copy()


def _parse_weights(raw: str) -> dict[str, float]:
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    w = json.loads(cleaned)
    keys = {"alpha", "beta", "gamma", "delta"}
    if not keys.issubset(w):
        raise ValueError(f"Missing keys in weight response: {w}")
    w = {k: float(w[k]) for k in keys}
    total = sum(w.values())
    if not (0.98 <= total <= 1.02):
        raise ValueError(f"Weights do not sum to 1.0: {total}")
    # Normalize to exactly 1.0
    return {k: round(v / total, 4) for k, v in w.items()}

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
