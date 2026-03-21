from dataclasses import dataclass
from skill_intelligence_service.models import SkillDNA

from .graph import build_graph
from .engine import run_selection, filter_valid_skills
from .reasoning import generate_reasoning, infer_weights
from .scorer import compute_scores
from .models import LearningPath


@dataclass
class EngineResult:
    learning_path: LearningPath
    graph: object
    scores: dict
    weights: dict


def run_engine(
    skill_dna: SkillDNA,
    proficiency: dict[str, float] | None = None,
    top_k: int = 3,
) -> EngineResult:
    resolved_proficiency = _resolve_proficiency(skill_dna, proficiency)

    G = build_graph(
        importance=skill_dna.importance,
        confidence=skill_dna.confidence,
        proficiency=resolved_proficiency,
    )

    weights = infer_weights(
        importance=skill_dna.importance,
        confidence=skill_dna.confidence,
        proficiency=resolved_proficiency,
    )

    scores = compute_scores(G, weights)
    valid_skills = filter_valid_skills(G)
    reasoning = generate_reasoning(G, scores, valid_skills)
    next_skills, roadmap = run_selection(G, reasoning, weights, top_k)

    return EngineResult(
        learning_path=LearningPath(
            next_skills=next_skills,
            roadmap=roadmap,
            reasoning=reasoning,
        ),
        graph=G,
        scores=scores,
        weights=weights,
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
