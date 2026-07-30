"""
Knowledge Graph - Visual concept map showing relationships.

Uses AI to identify relationships between concepts and renders
an interactive network graph with mastery overlay.
"""

from __future__ import annotations

import json
import os
from google import genai


RELATIONSHIP_PROMPT = """Given these concepts from a study session, identify the relationships between them.

Concepts:
{concepts_list}

For each pair of related concepts, describe the relationship type:
- "prerequisite": A must be understood before B
- "related": A and B are related/connected topics
- "part_of": A is a component/part of B
- "example": A is an example of B
- "causes": A causes or leads to B

Return as a JSON array of relationships:
[
    {{"source": "Concept A", "target": "Concept B", "type": "prerequisite", "label": "required for"}},
    {{"source": "Concept C", "target": "Concept D", "type": "related", "label": "connects to"}}
]

Only include relationships that genuinely exist. Return 3-10 relationships.
Return ONLY the JSON array, no other text."""


def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()



def extract_relationships(
    concepts: list[dict],
    model_name: str = "gemini-2.0-flash",
) -> list[dict]:
    """
    Extract relationships between concepts using AI.

    Args:
        concepts: List of concept dictionaries with name and description.
        model_name: Gemini model to use.

    Returns:
        List of relationship dicts with source, target, type, label.
    """
    if len(concepts) < 2:
        return []

    concepts_list = "\n".join(
        f"- {c['name']}: {c.get('description', '')}"
        for c in concepts
    )

    prompt = RELATIONSHIP_PROMPT.format(concepts_list=concepts_list)

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        relationships = json.loads(response_text)
        return relationships

    except Exception:
        # Generate basic relationships as fallback
        return _generate_fallback_relationships(concepts)


def _generate_fallback_relationships(concepts: list[dict]) -> list[dict]:
    """Generate simple sequential relationships as fallback."""
    relationships = []
    for i in range(len(concepts) - 1):
        relationships.append({
            "source": concepts[i]["name"],
            "target": concepts[i + 1]["name"],
            "type": "related",
            "label": "related to",
        })
    return relationships


def build_graph_data(
    concepts: list[dict],
    relationships: list[dict],
    concept_states: dict | None = None,
) -> dict:
    """
    Build graph data structure for Plotly visualization.

    Args:
        concepts: List of concept dictionaries.
        relationships: List of relationship dicts.
        concept_states: Optional concept states for mastery overlay.

    Returns:
        Dict with nodes and edges for visualization.
    """
    # Build nodes
    nodes = []
    for i, concept in enumerate(concepts):
        name = concept["name"]
        mastery = 0.0
        if concept_states and name in concept_states:
            mastery = concept_states[name].mastery_score

        # Color based on mastery
        if mastery >= 0.8:
            color = "#2ECC71"  # Green
        elif mastery >= 0.5:
            color = "#F39C12"  # Orange
        elif mastery > 0:
            color = "#E74C3C"  # Red
        else:
            color = "#BDC3C7"  # Grey (not attempted)

        # Size based on importance
        importance = concept.get("importance", "medium")
        size_map = {"high": 40, "medium": 30, "low": 20}
        size = size_map.get(importance, 30)

        nodes.append({
            "id": name,
            "label": name,
            "mastery": mastery,
            "color": color,
            "size": size,
            "description": concept.get("description", ""),
        })

    # Build edges
    edges = []
    for rel in relationships:
        edge_color_map = {
            "prerequisite": "#E74C3C",
            "related": "#3498DB",
            "part_of": "#9B59B6",
            "example": "#1ABC9C",
            "causes": "#E67E22",
        }
        edges.append({
            "source": rel["source"],
            "target": rel["target"],
            "type": rel.get("type", "related"),
            "label": rel.get("label", ""),
            "color": edge_color_map.get(rel.get("type", "related"), "#3498DB"),
        })

    return {"nodes": nodes, "edges": edges}
