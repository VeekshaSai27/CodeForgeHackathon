import json
import re

import networkx as nx
from dotenv import load_dotenv

from .base_graph import build_base_graph
from shared.gemini_pool import generate_with_retry

load_dotenv()

_EXPANSION_PROMPT = """
You are a skill dependency expert.

Given a list of unknown skills, return a JSON object that:
1. Lists each unknown skill as a node
2. Infers prerequisite edges from existing known skills or other unknown skills

Known skills in the graph: {known_skills}
Unknown skills to expand: {unknown_skills}

Return ONLY valid JSON in this exact format:
{{
  "nodes": [
    {{"skill": "Skill Name", "importance": 0.7}}
  ],
  "edges": [
    {{"from": "Prerequisite Skill", "to": "Skill Name"}}
  ]
}}
"""


def build_graph(
    importance: dict[str, float],
    confidence: dict[str, float],
    proficiency: dict[str, float],
) -> nx.DiGraph:
    G = build_base_graph()

    all_skills = set(importance.keys()) | set(confidence.keys()) | set(proficiency.keys())
    known = set(G.nodes)
    unknown = all_skills - known

    if unknown:
        _expand_graph(G, unknown, known)

    for skill in all_skills:
        if skill not in G:
            G.add_node(skill, importance=0.5, proficiency=0.0, confidence=0.0)

        if skill in importance:
            G.nodes[skill]["importance"] = importance[skill]
        if skill in confidence:
            G.nodes[skill]["confidence"] = confidence[skill]
        if skill in proficiency:
            G.nodes[skill]["proficiency"] = proficiency[skill]

    return G


def _expand_graph(G: nx.DiGraph, unknown: set[str], known: set[str]) -> None:
    prompt = _EXPANSION_PROMPT.format(
        known_skills=sorted(known),
        unknown_skills=sorted(unknown),
    )

    try:
        raw = generate_with_retry(prompt, temperature=0.2)
        data = _parse_expansion(raw)

        for node in data.get("nodes", []):
            skill = node["skill"]
            imp = float(node.get("importance", 0.5))
            if skill not in G:
                G.add_node(skill, importance=imp, proficiency=0.0, confidence=0.0)

        for edge in data.get("edges", []):
            src, dst = edge["from"], edge["to"]
            if src in G and dst in G:
                G.add_edge(src, dst)

    except Exception as e:
        print(f"⚠️ Graph expansion failed: {e}. Unknown skills added with defaults.")
        for skill in unknown:
            if skill not in G:
                G.add_node(skill, importance=0.5, proficiency=0.0, confidence=0.0)


def _parse_expansion(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(cleaned)
