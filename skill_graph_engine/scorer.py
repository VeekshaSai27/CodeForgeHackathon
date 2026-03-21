import networkx as nx

# Default fallback weights
_DEFAULTS = {"alpha": 0.4, "beta": 0.3, "gamma": 0.2, "delta": 0.1}


def compute_scores(
    G: nx.DiGraph,
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """
    Compute Skill Pressure Score for every node in the graph.

    Score = α·Importance + β·(1 - Proficiency) + γ·DependencyCentrality - δ·Confidence

    Args:
        G:       Skill dependency graph with node attributes
        weights: Dict with keys alpha, beta, gamma, delta (inferred or default)

    Returns:
        dict mapping skill -> score (0.0 to 1.0)
    """
    w = weights or _DEFAULTS
    alpha = w.get("alpha", _DEFAULTS["alpha"])
    beta  = w.get("beta",  _DEFAULTS["beta"])
    gamma = w.get("gamma", _DEFAULTS["gamma"])
    delta = w.get("delta", _DEFAULTS["delta"])

    centrality = _compute_centrality(G)

    scores = {}
    for skill in G.nodes:
        attrs = G.nodes[skill]
        importance    = attrs.get("importance", 0.5)
        proficiency   = attrs.get("proficiency", 0.0)
        confidence    = attrs.get("confidence", 0.0)
        dep_centrality = centrality.get(skill, 0.0)

        raw = (
            alpha * importance
            + beta  * (1.0 - proficiency)
            + gamma * dep_centrality
            - delta * confidence
        )

        scores[skill] = round(max(0.0, min(1.0, raw)), 4)

    return scores


def _compute_centrality(G: nx.DiGraph) -> dict[str, float]:
    """
    Compute normalized betweenness centrality for all nodes.
    Falls back to in-degree centrality if graph has no edges.
    """
    if G.number_of_edges() == 0:
        return dict.fromkeys(G.nodes, 0.0)

    raw = nx.betweenness_centrality(G, normalized=True)

    max_val = max(raw.values()) if raw else 1.0
    if max_val == 0.0:
        return dict.fromkeys(G.nodes, 0.0)

    return {skill: round(v / max_val, 4) for skill, v in raw.items()}
