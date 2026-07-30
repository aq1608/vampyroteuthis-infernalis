"""
Knowledge Graph Page - Interactive concept map visualization.

Shows how concepts relate to each other with mastery overlay,
helping students understand the big picture of what they're learning.
"""

from __future__ import annotations

import math
import streamlit as st
import plotly.graph_objects as go

from quiz_engine.knowledge_graph import extract_relationships, build_graph_data


def render_graph_page():
    """Render the knowledge graph visualization."""
    st.markdown("### Knowledge Graph")
    st.caption(
        "See how concepts connect to each other. "
        "Colors show your mastery level."
    )

    concepts = st.session_state.get("concepts", [])
    engine = st.session_state.get("adaptive_engine")

    if not concepts or len(concepts) < 2:
        st.info("Complete a quiz with 2+ concepts to see your knowledge graph.")
        if st.button("Back to Home"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # Generate or load relationships
    if "graph_relationships" not in st.session_state:
        with st.spinner("Mapping concept relationships..."):
            relationships = extract_relationships(concepts)
            st.session_state.graph_relationships = relationships
    else:
        relationships = st.session_state.graph_relationships

    # Build graph data
    concept_states = engine.concept_states if engine else {}
    graph_data = build_graph_data(concepts, relationships, concept_states)

    # Render the graph
    _render_network_graph(graph_data)

    # Legend
    st.divider()
    _render_legend()

    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Results"):
            st.session_state.page = "results"
            st.rerun()
    with col2:
        if st.button("Refresh Graph"):
            st.session_state.pop("graph_relationships", None)
            st.rerun()



def _render_network_graph(graph_data: dict):
    """Render an interactive network graph using Plotly."""
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]

    if not nodes:
        st.info("No graph data available.")
        return

    # Circular layout
    n = len(nodes)
    positions = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        positions[node["id"]] = (math.cos(angle), math.sin(angle))

    # Create edge traces
    edge_traces = []
    for edge in edges:
        if edge["source"] in positions and edge["target"] in positions:
            x0, y0 = positions[edge["source"]]
            x1, y1 = positions[edge["target"]]
            edge_traces.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(width=2, color=edge.get("color", "#ccc")),
                hoverinfo="text",
                text=f"{edge['source']} → {edge['target']}: {edge.get('label', '')}",
                showlegend=False,
            ))

    # Create node trace
    node_x = [positions[n["id"]][0] for n in nodes]
    node_y = [positions[n["id"]][1] for n in nodes]
    node_colors = [n["color"] for n in nodes]
    node_sizes = [n["size"] for n in nodes]
    node_texts = [
        f"<b>{n['label']}</b><br>"
        f"Mastery: {n['mastery']*100:.0f}%<br>"
        f"{n.get('description', '')}"
        for n in nodes
    ]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color="white"),
        ),
        text=[n["label"] for n in nodes],
        textposition="top center",
        textfont=dict(size=11, color="#2C3E50"),
        hovertext=node_texts,
        hoverinfo="text",
        showlegend=False,
    )

    # Build figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=450,
        margin=dict(t=20, b=20, l=20, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_legend():
    """Render color legend for the graph."""
    cols = st.columns(4)
    with cols[0]:
        st.markdown("🟢 Mastered (80%+)")
    with cols[1]:
        st.markdown("🟠 Moderate (50-79%)")
    with cols[2]:
        st.markdown("🔴 Weak (<50%)")
    with cols[3]:
        st.markdown("⚪ Not attempted")
