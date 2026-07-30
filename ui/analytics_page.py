"""
Learning Analytics Page - Visualize progress over time.

Shows:
- Performance trend line chart
- Retention prediction curves
- Study pattern analysis
- Strengths/weaknesses summary
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go


def render_analytics_page():
    """Render the learning analytics dashboard."""
    analytics = st.session_state.get("analytics")

    st.markdown("### Learning Analytics")

    if not analytics or not analytics.sessions:
        st.info(
            "Complete a few quizzes to see your learning analytics! "
            "Data builds up over time to show your improvement."
        )
        if st.button("Back to Home"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # Key metrics row
    _render_key_metrics(analytics)
    st.divider()

    # Performance trend
    _render_performance_trend(analytics)
    st.divider()

    # Retention forecast
    _render_retention_forecast(analytics)
    st.divider()

    # Strengths and weaknesses
    _render_strengths_weaknesses(analytics)
    st.divider()

    # Study patterns
    _render_study_patterns(analytics)

    # Navigation
    st.divider()
    if st.button("Back to Home"):
        st.session_state.page = "upload"
        st.rerun()



def _render_key_metrics(analytics):
    """Render the top-level metrics."""
    cols = st.columns(4)

    with cols[0]:
        st.metric(
            "Total Sessions",
            len(analytics.sessions),
        )
    with cols[1]:
        improvement = analytics.get_improvement_rate()
        st.metric(
            "Improvement",
            f"{improvement:+.1f}%",
            delta=f"{'Improving' if improvement > 0 else 'Practice more'}",
        )
    with cols[2]:
        streak = analytics.get_study_streak_days()
        st.metric("Study Streak", f"{streak} days")
    with cols[3]:
        best_time = analytics.get_optimal_study_time()
        st.metric("Best Study Time", best_time)


def _render_performance_trend(analytics):
    """Render performance trend chart."""
    st.markdown("#### Performance Over Time")

    trend = analytics.get_performance_trend()
    if len(trend) < 2:
        st.caption("Complete more quizzes to see your trend.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[t["session"] for t in trend],
        y=[t["score"] for t in trend],
        mode="lines+markers",
        name="Score %",
        line=dict(color="#6C63FF", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(108, 99, 255, 0.1)",
    ))

    fig.update_layout(
        yaxis_title="Score %",
        xaxis_title="Session",
        yaxis_range=[0, 100],
        height=300,
        margin=dict(t=10, b=40, l=40, r=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_retention_forecast(analytics):
    """Render predicted retention curves."""
    st.markdown("#### Retention Forecast")
    st.caption(
        "Predicted memory retention based on the Ebbinghaus forgetting curve"
    )

    concepts = list(analytics.concept_timeline.keys())
    if not concepts:
        st.caption("No concept data yet.")
        return

    forecast = analytics.get_retention_forecast(concepts[:5])

    fig = go.Figure()
    colors = ["#6C63FF", "#4ECDC4", "#FF6B6B", "#F39C12", "#9B59B6"]

    for i, concept_data in enumerate(forecast):
        predictions = concept_data["predictions"]
        fig.add_trace(go.Scatter(
            x=[p["hours"] for p in predictions],
            y=[p["retention"] for p in predictions],
            mode="lines+markers",
            name=concept_data["concept"],
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6),
        ))

    # Add optimal review line
    fig.add_hline(
        y=70, line_dash="dash", line_color="gray",
        annotation_text="Review threshold (70%)",
    )

    fig.update_layout(
        yaxis_title="Predicted Retention %",
        xaxis_title="Hours from now",
        yaxis_range=[0, 100],
        height=350,
        margin=dict(t=10, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_strengths_weaknesses(analytics):
    """Render strengths and weaknesses analysis."""
    st.markdown("#### Strengths & Weaknesses")

    data = analytics.get_strengths_weaknesses()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Strengths**")
        if data["strengths"]:
            for item in data["strengths"]:
                st.markdown(
                    f"- {item['concept']} "
                    f"({item['mastery']*100:.0f}%)"
                )
        else:
            st.caption("Keep studying to build strengths!")

    with col2:
        st.markdown("**Needs Work**")
        if data["weaknesses"]:
            for item in data["weaknesses"]:
                st.markdown(
                    f"- {item['concept']} "
                    f"({item['mastery']*100:.0f}%)"
                )
        else:
            st.caption("No weaknesses identified!")


def _render_study_patterns(analytics):
    """Render study pattern insights."""
    st.markdown("#### Study Patterns")

    if not analytics.study_times:
        st.caption("Study more to see patterns.")
        return

    # Hour distribution
    hour_counts = {}
    for hour in analytics.study_times:
        hour_counts[hour] = hour_counts.get(hour, 0) + 1

    hours = list(range(24))
    counts = [hour_counts.get(h, 0) for h in hours]
    labels = [f"{h:02d}:00" for h in hours]

    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=counts,
            marker_color="#6C63FF",
        )
    ])
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Sessions",
        height=250,
        margin=dict(t=10, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)
