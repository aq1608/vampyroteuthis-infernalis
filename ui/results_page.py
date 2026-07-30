"""
Results Page - Score dashboard with gamification, study guide, and export.

Features:
- Animated score card
- Per-concept mastery visualization
- XP/badge summary for this quiz
- AI-generated study guide download
- Progress export (JSON)
- Spaced repetition scheduling
"""

from __future__ import annotations

import base64
import streamlit as st
import plotly.graph_objects as go

from quiz_engine.study_guide import generate_study_guide
from quiz_engine.persistence import export_progress, create_quiz_summary
from quiz_engine.curriculum import (
    get_next_topic,
    get_path_progress,
    is_last_topic_in_path,
    get_topics,
)
from quiz_engine.certificate import (
    generate_certificate_svg,
    certificate_filename,
    compute_path_average_score,
)
from ui.styles import render_score_card, render_mastery_bar


def _render_certificate(path_name: str):
    """Render a downloadable completion certificate for a finished path."""
    gam = st.session_state.get("gamification")
    student_name = st.session_state.get("player_name", "Anonymous Learner")
    topics = get_topics(path_name)
    topic_names = [t["name"] for t in topics]

    avg_score = compute_path_average_score(
        st.session_state.get("quiz_history", []), topic_names
    )

    svg = generate_certificate_svg(
        student_name=student_name,
        path_name=path_name,
        topics_completed=len(topics),
        average_score=avg_score,
        total_xp=getattr(gam, "total_xp", None) if gam else None,
        level_title=gam.current_level["title"] if gam else None,
    )

    st.markdown("**You earned a Certificate of Completion!**")
    # Preview the certificate inline via a base64 data URI (reliable for SVG)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    st.markdown(
        f'<img src="data:image/svg+xml;base64,{b64}" '
        f'style="width:100%; border-radius:12px;" alt="Certificate"/>',
        unsafe_allow_html=True,
    )
    st.download_button(
        label="Download Certificate (.svg)",
        data=svg,
        file_name=certificate_filename(student_name, path_name),
        mime="image/svg+xml",
        key="btn_download_cert",
    )
    st.caption(
        "Tip: open the SVG in a browser and print to PDF, or set your name "
        "in the sidebar before downloading."
    )


def _mark_topic_completed(path_name: str, topic_name: str):
    """Record a curriculum topic as completed for guided path tracking."""
    completed = st.session_state.setdefault("completed_topics", {})
    path_list = completed.setdefault(path_name, [])
    if topic_name not in path_list:
        path_list.append(topic_name)


def _render_guided_path_section():
    """
    Show guided-path progress and a button to continue to the next topic.

    Only shown when the completed quiz was launched from a curriculum path.
    """
    ctx = st.session_state.get("path_context")
    if not ctx:
        return

    path_name = ctx["path"]
    topic_name = ctx["topic"]

    # Mark this topic complete
    _mark_topic_completed(path_name, topic_name)

    st.markdown("### Guided Path")
    st.caption(f"Path: **{path_name}**")

    # Progress through the path
    completed = st.session_state.get("completed_topics", {}).get(path_name, [])
    progress = get_path_progress(path_name, completed)
    st.progress(progress["percentage"] / 100)
    st.markdown(
        f"**{progress['completed']}/{progress['total']}** topics complete "
        f"({progress['percentage']:.0f}%)"
    )

    # Suggest the next topic, or celebrate completion
    next_topic = get_next_topic(path_name, topic_name)

    if progress["is_complete"]:
        st.success(f"You've completed the entire '{path_name}' path! Well done.")
        _render_certificate(path_name)
    elif next_topic:
        st.info(f"Up next: **{next_topic['name']}** ({next_topic['level']})")
        if st.button(
            f"Continue to '{next_topic['name']}'",
            type="primary",
            key="btn_next_topic",
        ):
            # Import here to avoid any circular import at module load time
            from ui.upload_page import launch_curriculum_topic, _configure_gemini

            if not _configure_gemini():
                st.error("Please set your Gemini API key on the home page first.")
            else:
                language = st.session_state.get("language", "English")
                launch_curriculum_topic(path_name, next_topic, language)
    elif is_last_topic_in_path(path_name, topic_name):
        st.success(f"That was the last topic in '{path_name}'. Review any topic to reinforce it.")


def _render_score_section(engine):
    """Render the main score card."""
    score = engine.get_overall_score()

    st.markdown(
        render_score_card(
            score["total_correct"],
            score["total_attempts"],
            score["percentage"],
        ),
        unsafe_allow_html=True,
    )
    return score


def _render_xp_summary():
    """Render XP earned this quiz and badges."""
    gam = st.session_state.gamification
    answers = st.session_state.answers

    total_xp_this_quiz = sum(a.get("xp_earned", 0) for a in answers)

    cols = st.columns(4)
    with cols[0]:
        st.metric("XP Earned", f"+{total_xp_this_quiz}")
    with cols[1]:
        st.metric("Total XP", gam.total_xp)
    with cols[2]:
        st.metric("Level", f"{gam.current_level['level']} {gam.current_level['title']}")
    with cols[3]:
        st.metric("Best Streak", gam.best_streak)

    # Show new badges earned
    new_badges = []
    for badge_id in gam.badges_earned:
        info = gam.get_badge_info(badge_id)
        new_badges.append(info)

    if new_badges:
        st.markdown("**Badges:**")
        badge_html = " ".join(
            f'<span class="badge-earned">{b["emoji"]} {b["name"]}</span>'
            for b in new_badges
        )
        st.markdown(badge_html, unsafe_allow_html=True)



def _render_concept_breakdown(engine):
    """Render per-concept performance with mastery bars."""
    st.markdown("### Performance by Concept")

    concepts = list(engine.concept_states.values())
    if not concepts:
        st.info("No concept data available.")
        return

    # Plotly chart
    names = [c.name for c in concepts]
    scores = [c.mastery_score * 100 for c in concepts]
    colors = [
        "#2ECC71" if s >= 80 else "#F39C12" if s >= 50 else "#E74C3C"
        for s in scores
    ]

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=scores,
            marker_color=colors,
            text=[f"{s:.0f}%" for s in scores],
            textposition="auto",
        )
    ])
    fig.update_layout(
        yaxis_title="Mastery %",
        yaxis_range=[0, 100],
        showlegend=False,
        height=300,
        margin=dict(t=10, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mastery bars
    for concept in concepts:
        st.markdown(
            render_mastery_bar(concept.mastery_score, concept.name),
            unsafe_allow_html=True,
        )


def _render_study_guide_section(engine):
    """Render study guide generation and download."""
    st.markdown("### Study Guide")

    if st.button("Generate AI Study Guide", type="primary", key="btn_study_guide"):
        with st.spinner("Creating your personalized study guide..."):
            guide = generate_study_guide(
                content=st.session_state.content or "",
                answers=st.session_state.answers,
                concept_states=engine.concept_states,
                language=st.session_state.get("language", "English"),
            )
            st.session_state.study_guide = guide

    if st.session_state.get("study_guide"):
        st.markdown(st.session_state.study_guide)
        st.download_button(
            label="Download Study Guide (.md)",
            data=st.session_state.study_guide,
            file_name="study_guide.md",
            mime="text/markdown",
        )



def _render_export_section():
    """Render progress export and history."""
    st.markdown("### Progress & History")

    # Export progress
    progress_json = export_progress(
        gamification=st.session_state.gamification,
        spaced_rep=st.session_state.spaced_rep,
        quiz_history=st.session_state.quiz_history,
    )
    st.download_button(
        label="Download Progress (.json)",
        data=progress_json,
        file_name="quiz_progress.json",
        mime="application/json",
    )

    # Quiz history
    if st.session_state.quiz_history:
        with st.expander("Quiz History"):
            for i, quiz in enumerate(reversed(st.session_state.quiz_history[-10:])):
                st.markdown(
                    f"**{quiz.get('timestamp', 'Unknown')[:10]}** - "
                    f"{quiz.get('score_percentage', 0):.0f}% "
                    f"({quiz.get('score_correct', 0)}/{quiz.get('num_questions', 0)}) "
                    f"| {quiz.get('language', 'English')}"
                )


def _render_recommendations(engine):
    """Render study recommendations."""
    st.markdown("### Recommendations")

    weak = engine.get_weakest_concepts(top_n=3)
    review = engine.get_concepts_for_review()

    if review:
        st.warning("**Flagged for review:**")
        for concept in review:
            st.markdown(f"- **{concept.name}** - needs more practice")

    if weak and weak[0].mastery_score < 0.8:
        st.info("**Focus your study on:**")
        for concept in weak:
            if concept.mastery_score < 0.8:
                st.markdown(
                    f"- **{concept.name}** "
                    f"({concept.mastery_score * 100:.0f}% mastery)"
                )
    else:
        st.success("Great job! You've demonstrated strong understanding across all concepts.")


def render_results_page():
    """Render the full results dashboard."""
    engine = st.session_state.adaptive_engine

    if not engine:
        st.error("No quiz data available.")
        if st.button("Start New Quiz"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # Complete gamification tracking
    gam = st.session_state.gamification
    concept_masteries = {
        name: state.mastery_score
        for name, state in engine.concept_states.items()
    }
    gam.complete_quiz(concept_masteries)

    # Track non-English quiz
    if st.session_state.get("language", "English") != "English":
        gam.record_non_english_quiz()

    # Update spaced repetition schedule
    st.session_state.spaced_rep.add_concepts_from_quiz(engine.concept_states)

    # Save quiz to history
    score = engine.get_overall_score()
    summary = create_quiz_summary(
        content_source=st.session_state.content[:100] if st.session_state.content else "Unknown",
        concepts=st.session_state.concepts,
        answers=st.session_state.answers,
        overall_score=score,
        language=st.session_state.get("language", "English"),
    )
    # Only add if not already added (avoid duplicates on rerun)
    if not st.session_state.quiz_history or (
        st.session_state.quiz_history[-1].get("timestamp") != summary["timestamp"]
    ):
        st.session_state.quiz_history.append(summary)

    st.markdown("## Quiz Results")

    # Score card
    _render_score_section(engine)
    st.divider()

    # Guided path progress (only for curriculum-launched quizzes)
    _render_guided_path_section()
    if st.session_state.get("path_context"):
        st.divider()

    # XP and gamification
    _render_xp_summary()
    st.divider()

    # Concept breakdown
    _render_concept_breakdown(engine)
    st.divider()

    # Recommendations
    _render_recommendations(engine)
    st.divider()

    # Study guide
    _render_study_guide_section(engine)
    st.divider()

    # Export and history
    _render_export_section()
    st.divider()

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start New Quiz", type="primary"):
            st.session_state.page = "upload"
            st.session_state.content = None
            st.session_state.concepts = []
            st.session_state.questions = []
            st.session_state.current_question_idx = 0
            st.session_state.answers = []
            st.session_state.adaptive_engine = None
            st.session_state.quiz_complete = False
            st.session_state.path_context = None
            st.session_state.pop("study_guide", None)
            st.rerun()
    with col2:
        if st.button("Re-quiz Weak Areas"):
            weak = [
                c for c in engine.concept_states.values()
                if c.mastery_score < 0.8
            ]
            if weak:
                st.info("Re-quiz feature: Start a new quiz on the same topic to practice!")
            else:
                st.success("No weak areas! You've mastered everything.")
