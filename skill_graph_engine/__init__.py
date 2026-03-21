from skill_intelligence_service.models import SkillDNA

from .graph import build_graph
from .engine import run_selection, filter_valid_skills, compute_scores
from .reasoning import generate_reasoning
from .scorer import compute_scores
from .models import LearningPath


def run_engine(
    skill_dna: SkillDNA,
    proficiency: dict[str, float] | None = None,
    top_k: int = 3,
) -> LearningPath:
    """
    Main entry point for the Skill Graph Decision Engine.

    Args:
        skill_dna:   Output from skill_intelligence_service (skills, importance, confidence)
        proficiency: Output from skill_validation_service (skill -> proficiency score 0-1)
                     Falls back to resume confidence, then 0.0 per design spec.
        top_k:       Number of immediate next skills to recommend (default: 3)

    Returns:
        LearningPath with next_skills, roadmap, and reasoning
    """
    resolved_proficiency = _resolve_proficiency(skill_dna, proficiency)

    G = build_graph(
        importance=skill_dna.importance,
        confidence=skill_dna.confidence,
        proficiency=resolved_proficiency,
    )

    scores = compute_scores(G)
    valid_skills = filter_valid_skills(G)
    reasoning = generate_reasoning(G, scores, valid_skills)
    next_skills, roadmap = run_selection(G, reasoning, top_k)

    return LearningPath(
        next_skills=next_skills,
        roadmap=roadmap,
        reasoning=reasoning,
    )


def _resolve_proficiency(
    skill_dna: SkillDNA,
    proficiency: dict[str, float] | None,
) -> dict[str, float]:
    """
    Resolve proficiency per design spec priority:
    1. Skill Validation Service output (highest priority)
    2. Resume-based confidence from SkillDNA
    3. Default = 0.0
    """
    resolved = {}
    for skill in skill_dna.skills:
        if proficiency and skill in proficiency:
            resolved[skill] = proficiency[skill]
        elif skill in skill_dna.confidence:
            resolved[skill] = skill_dna.confidence[skill]
        else:
            resolved[skill] = 0.0
    return resolved
