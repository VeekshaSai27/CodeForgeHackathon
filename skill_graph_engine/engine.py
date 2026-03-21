import networkx as nx

from .models import RoadmapItem
from .scorer import compute_scores

# Prerequisites are "satisfied" if proficiency meets this threshold
PROFICIENCY_THRESHOLD = 0.4


def get_prerequisites(G: nx.DiGraph, skill: str) -> list[str]:
    """Return direct prerequisite skills (nodes with edges pointing TO this skill)."""
    return list(G.predecessors(skill))


def prerequisites_satisfied(G: nx.DiGraph, skill: str) -> bool:
    """
    A skill is unlocked if ALL its prerequisites have proficiency >= threshold.
    Skills with no prerequisites are always unlocked.
    """
    prereqs = get_prerequisites(G, skill)
    if not prereqs:
        return True
    return all(
        G.nodes[p].get("proficiency", 0.0) >= PROFICIENCY_THRESHOLD
        for p in prereqs
    )


def filter_valid_skills(G: nx.DiGraph) -> list[str]:
    """Return all skills whose prerequisites are satisfied."""
    return [skill for skill in G.nodes if prerequisites_satisfied(G, skill)]


def build_roadmap(
    G: nx.DiGraph,
    scores: dict[str, float],
    valid_skills: list[str],
    reasoning: dict[str, str],
) -> list[RoadmapItem]:
    """
    Build full ordered roadmap from valid skills, sorted by score descending.
    Each item includes skill, score, reason, and its prerequisites.
    """
    sorted_skills = sorted(valid_skills, key=lambda s: scores[s], reverse=True)

    return [
        RoadmapItem(
            skill=skill,
            score=scores[skill],
            reason=reasoning.get(skill, ""),
            prerequisites=get_prerequisites(G, skill),
        )
        for skill in sorted_skills
    ]


def select_next_skills(
    scores: dict[str, float],
    valid_skills: list[str],
    top_k: int = 3,
) -> list[str]:
    """Select top-K immediate skills to learn next from valid skills."""
    ranked = sorted(valid_skills, key=lambda s: scores[s], reverse=True)
    return ranked[:top_k]


def run_selection(
    G: nx.DiGraph,
    reasoning: dict[str, str],
    top_k: int = 3,
) -> tuple[list[str], list[RoadmapItem]]:
    """
    Full selection pipeline:
    1. Compute scores
    2. Filter valid skills
    3. Select top-K next skills
    4. Build full roadmap

    Returns:
        (next_skills, roadmap)
    """
    scores = compute_scores(G)
    valid_skills = filter_valid_skills(G)
    next_skills = select_next_skills(scores, valid_skills, top_k)
    roadmap = build_roadmap(G, scores, valid_skills, reasoning)

    return next_skills, roadmap
