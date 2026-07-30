"""
Upload Page - Content input interface with polished UI.

Features:
- Hero section with animated gradient
- Three input modes: PDF, text, topic
- Multi-language support
- Progress import
- Spaced repetition review launcher
"""

from __future__ import annotations

import base64
import json
import streamlit as st
import os
from google import genai

from quiz_engine.content_parser import parse_pdf, parse_text
from quiz_engine.concept_extractor import extract_concepts
from quiz_engine.question_generator import generate_quiz_batch
from quiz_engine.adaptive_logic import AdaptiveEngine
from quiz_engine.persistence import import_progress
from quiz_engine.curriculum import (
    get_learning_paths,
    get_path_info,
    get_topics,
    get_topic,
    build_topic_prompt,
    count_total_topics,
    get_path_progress,
    get_first_incomplete_topic,
)
from quiz_engine.certificate import (
    generate_certificate_svg,
    certificate_filename,
    compute_path_average_score,
)
from ui.styles import render_hero, render_feature_cards


def _render_curriculum_certificate(path_name: str):
    """Render a downloadable certificate for a completed learning path."""
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
        key=f"btn_cert_{path_name}",
    )


def _configure_gemini() -> bool:
    """Configure Gemini API. Returns True if key is available."""
    api_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("api_key")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        return True
    return False


def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()



def _process_content(
    content: str,
    start_difficulty: str = "beginner",
    path_context: dict | None = None,
):
    """
    Extract concepts and generate initial quiz from content.

    Args:
        content: The study material to quiz on.
        start_difficulty: Starting difficulty level.
        path_context: Optional dict {"path": name, "topic": name} when the
            quiz was launched from a guided curriculum path. Used to suggest
            the next topic on the results page.
    """
    language = st.session_state.get("language", "English")

    with st.spinner("Extracting key concepts..."):
        concepts = extract_concepts(content, language=language)
        st.session_state.concepts = concepts

    with st.spinner("Generating your personalized quiz..."):
        questions = generate_quiz_batch(
            concepts=concepts,
            content=content,
            difficulty=start_difficulty,
            questions_per_concept=2,
            language=language,
        )
        st.session_state.questions = questions

    # Initialize adaptive engine
    engine = AdaptiveEngine()
    engine.register_concepts(concepts)
    st.session_state.adaptive_engine = engine
    st.session_state.content = content
    st.session_state.current_question_idx = 0
    st.session_state.answers = []
    st.session_state.quiz_complete = False

    # Track guided-path context (or clear it for non-curriculum quizzes)
    st.session_state.path_context = path_context

    # Navigate to quiz page
    st.session_state.page = "quiz"
    st.rerun()


def _render_api_key_input():
    """Render API key input if not set."""
    if not os.getenv("GEMINI_API_KEY"):
        with st.expander("API Key Setup", expanded=True):
            st.markdown(
                "Get your **free** API key at "
                "[aistudio.google.com/apikey](https://aistudio.google.com/apikey)"
            )
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                key="api_key_input",
                placeholder="Enter your API key here...",
            )
            if api_key:
                st.session_state.api_key = api_key
                st.success("API key set!")


def _render_review_section():
    """Render spaced repetition review section if items are due."""
    spaced_rep = st.session_state.spaced_rep
    due_items = spaced_rep.get_due_items()
    weak_items = spaced_rep.get_weak_items()

    if due_items or weak_items:
        st.divider()
        st.markdown("### Review Due")
        items_to_show = due_items if due_items else weak_items[:3]
        for item in items_to_show:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f"**{item.concept_name}** - "
                    f"{item.mastery_score*100:.0f}% mastery"
                )
            with col2:
                st.caption(f"{item.mastery_level}")

        if st.button("Start Review Quiz", key="btn_review"):
            st.info("Review mode coming soon! For now, re-quiz on the topic.")



def _render_import_section():
    """Render progress import section."""
    with st.expander("Import Progress"):
        uploaded = st.file_uploader(
            "Upload a progress file (.json)",
            type=["json"],
            key="progress_upload",
        )
        if uploaded and st.button("Load Progress", key="btn_import"):
            try:
                json_str = uploaded.read().decode("utf-8")
                data = import_progress(json_str)
                st.session_state.gamification = data["gamification"]
                st.session_state.spaced_rep = data["spaced_repetition"]
                st.session_state.quiz_history = data["quiz_history"]
                st.success("Progress loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load progress: {e}")


def launch_curriculum_topic(
    path_name: str,
    topic: dict,
    language: str,
    match_level: bool = False,
):
    """
    Generate study content for a curriculum topic and start its quiz.

    Shared by the curriculum tab and the guided "next topic" button on the
    results page. Requires the Gemini API key to be configured.
    """
    start_difficulty = topic["level"] if match_level else "beginner"
    with st.spinner(f"Preparing study material on '{topic['name']}'..."):
        client = _get_client()
        prompt = build_topic_prompt(topic, language=language)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        content = response.text
    _process_content(
        content,
        start_difficulty=start_difficulty,
        path_context={"path": path_name, "topic": topic["name"]},
    )


def _render_path_progress_panel(path_name: str):
    """Show the student's progress through the selected learning path."""
    completed = st.session_state.get("completed_topics", {}).get(path_name, [])
    progress = get_path_progress(path_name, completed)

    if progress["completed"] > 0:
        st.progress(progress["percentage"] / 100)
        st.caption(
            f"Path progress: {progress['completed']}/{progress['total']} topics "
            f"({progress['percentage']:.0f}%)"
        )

    # Per-topic checklist
    with st.expander("Path checklist", expanded=False):
        for item in progress["topics"]:
            mark = "[x]" if item["completed"] else "[ ]"
            st.markdown(f"{mark} **{item['name']}** ({item['level']})")

    return progress


def _render_curriculum_tab(language: str):
    """Render the pre-loaded AI/ML curriculum picker with guided path mode."""
    st.markdown(
        f"Pick a ready-made topic from the **AI/ML curriculum** "
        f"({count_total_topics()} topics across {len(get_learning_paths())} learning paths). "
        "Complete a topic and the next one is suggested automatically."
    )

    # Learning path selector
    paths = get_learning_paths()
    selected_path = st.selectbox(
        "Learning Path",
        paths,
        key="curriculum_path_select",
    )

    path_info = get_path_info(selected_path)
    if path_info.get("blurb"):
        st.caption(path_info["blurb"])

    # Progress panel for the selected path
    progress = _render_path_progress_panel(selected_path)

    # Guided mode: jump straight to the next uncompleted topic
    completed = st.session_state.get("completed_topics", {}).get(selected_path, [])
    resume_topic = get_first_incomplete_topic(selected_path, completed)
    if resume_topic and progress["completed"] > 0:
        st.info(f"Guided path: up next is **{resume_topic['name']}**")
        if st.button(
            f"Continue path -> {resume_topic['name']}",
            key="btn_resume_path",
            type="primary",
        ):
            if not _configure_gemini():
                st.error("Please enter your Gemini API key above.")
                return
            launch_curriculum_topic(selected_path, resume_topic, language)
    elif progress["is_complete"]:
        st.success(f"You've completed the entire '{selected_path}' path! Pick any topic to review.")
        _render_curriculum_certificate(selected_path)

    st.divider()

    # Manual topic selector for the chosen path
    topics = get_topics(selected_path)
    topic_labels = [f"{t['name']}  ({t['level']})" for t in topics]
    selected_label = st.selectbox(
        "Or choose any topic",
        topic_labels,
        key="curriculum_topic_select",
    )

    selected_idx = topic_labels.index(selected_label)
    selected_topic = topics[selected_idx]

    # Show a short preview of what will be covered
    with st.expander("What this quiz covers"):
        st.write(selected_topic["description"])

    # Optionally match the quiz start difficulty to the topic level
    match_level = st.checkbox(
        f"Start quiz at this topic's level ({selected_topic['level']})",
        value=False,
        key="curriculum_match_level",
        help="Otherwise the quiz starts at beginner and adapts up as you answer.",
    )

    if st.button("Generate Quiz from Curriculum", key="btn_curriculum", type="primary"):
        if not _configure_gemini():
            st.error("Please enter your Gemini API key above.")
            return
        launch_curriculum_topic(
            selected_path, selected_topic, language, match_level=match_level
        )


def render_upload_page():
    """Render the content upload/input page."""
    # Hero section
    render_hero()
    render_feature_cards()

    st.divider()

    # API Key
    _render_api_key_input()

    # Review section
    _render_review_section()

    # Main input
    st.markdown("### What do you want to study?")
    language = st.session_state.get("language", "English")
    if language != "English":
        st.info(f"Quiz will be generated in **{language}**")

    # Tab-based input options
    tab_curriculum, tab_pdf, tab_text, tab_topic = st.tabs(
        ["AI/ML Curriculum", "Upload PDF", "Paste Text", "Enter Topic"]
    )

    with tab_curriculum:
        _render_curriculum_tab(language)

    with tab_pdf:
        uploaded_file = st.file_uploader(
            "Upload a PDF (textbook chapter, notes, article)",
            type=["pdf"],
            key="pdf_upload",
        )
        if uploaded_file and st.button("Generate Quiz from PDF", key="btn_pdf", type="primary"):
            if not _configure_gemini():
                st.error("Please enter your Gemini API key above.")
                return
            content = parse_pdf(uploaded_file)
            if content.strip():
                _process_content(content)
            else:
                st.error("Could not extract text from this PDF.")

    with tab_text:
        raw_text = st.text_area(
            "Paste your study material here",
            height=200,
            placeholder="Paste a textbook excerpt, lecture notes, or article...",
            key="text_input",
        )
        if raw_text and st.button("Generate Quiz from Text", key="btn_text", type="primary"):
            if not _configure_gemini():
                st.error("Please enter your Gemini API key above.")
                return
            content = parse_text(raw_text)
            if content.strip():
                _process_content(content)
            else:
                st.error("Please enter some text.")

    with tab_topic:
        topic = st.text_input(
            "Enter a topic and AI will generate study content + quiz",
            placeholder="e.g. 'The French Revolution', 'Quantum Mechanics', 'Python decorators'",
            key="topic_input",
        )
        if topic and st.button("Generate Quiz from Topic", key="btn_topic", type="primary"):
            if not _configure_gemini():
                st.error("Please enter your Gemini API key above.")
                return
            with st.spinner("Generating study material..."):
                client = _get_client()
                lang_instruction = f" Write in {language}." if language != "English" else ""
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=(
                        f"Write a comprehensive educational summary (500-800 words) about: {topic}. "
                        f"Cover the key concepts, important details, and relationships between ideas. "
                        f"Write in a clear, textbook-like style suitable for studying.{lang_instruction}"
                    ),
                )
                content = response.text
            _process_content(content)

    # Import section at bottom
    st.divider()
    _render_import_section()
