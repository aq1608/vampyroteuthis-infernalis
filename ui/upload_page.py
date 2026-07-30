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
import os
import time
import streamlit as st

from quiz_engine.collaborative import import_quiz_code
from quiz_engine.content_parser import parse_pdf, parse_text
from quiz_engine.question_generator import generate_full_quiz
from quiz_engine.adaptive_logic import AdaptiveEngine
from quiz_engine.persistence import import_progress
from quiz_engine.llm import generate_text, GenerationError
from quiz_engine.manual_quiz import validate_question, build_quiz_from_questions
from quiz_engine.question_bank import list_bank_topics, get_bank_questions, total_bank_questions
from quiz_engine.curriculum import (
    get_learning_paths,
    get_path_info,
    get_topics,
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

    try:
        # Single API call generates BOTH concepts and questions (quota-friendly)
        with st.spinner("Building your personalized quiz..."):
            quiz = generate_full_quiz(
                content=content,
                difficulty=start_difficulty,
                num_concepts=4,
                questions_per_concept=2,
                language=language,
            )
            st.session_state.concepts = quiz["concepts"]
            st.session_state.questions = quiz["questions"]
    except GenerationError as e:
        st.error(str(e))
        return
    except Exception as e:  # noqa: BLE001 - surface any unexpected failure gracefully
        st.error(f"Could not generate the quiz. {e}")
        return

    if not st.session_state.get("questions") or not st.session_state.get("concepts"):
        st.error(
            "The AI returned an empty quiz. Try again, pick a different topic, "
            "or use the 'Build Manually' tab."
        )
        return

    _begin_quiz(
        concepts=st.session_state.concepts,
        questions=st.session_state.questions,
        content=content,
        path_context=path_context,
    )


def _begin_quiz(
    concepts: list[dict],
    questions: list[dict],
    content: str | None = None,
    path_context: dict | None = None,
    imported_quiz_data: dict | None = None,
):
    """
    Set up session state for a new quiz and navigate to it.

    Shared by both the AI path (_process_content) and the manual builder, so a
    quiz behaves identically no matter how its questions were created.
    """
    st.session_state.concepts = concepts
    st.session_state.questions = questions

    engine = AdaptiveEngine()
    engine.register_concepts(concepts)
    st.session_state.adaptive_engine = engine
    st.session_state.content = content
    st.session_state.current_question_idx = 0
    st.session_state.answers = []
    st.session_state.quiz_complete = False
    # New quiz: allow its results to be recorded once when it finishes, and
    # snapshot the badges already owned so results can show only new ones.
    st.session_state.results_recorded = False
    st.session_state.badges_at_quiz_start = list(
        st.session_state.gamification.badges_earned
    )
    st.session_state.quiz_start_time = time.time()

    # Track guided-path context (or clear it for non-curriculum quizzes)
    st.session_state.path_context = path_context
    # Shared-quiz data (carries a leaderboard) when launched from a quiz code,
    # or None for a locally-created quiz.
    st.session_state.imported_quiz_data = imported_quiz_data

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



def _render_shared_quiz_section():
    """Render the 'play a shared quiz' loader (collaborative mode)."""
    with st.expander("Play a shared quiz"):
        st.caption(
            "Paste a quiz code a friend shared to take the exact same quiz and "
            "add your score to its leaderboard. No API key needed."
        )
        code = st.text_input(
            "Shared quiz code",
            key="shared_code_input",
            placeholder="QUIZ-XXXXXXXX-...",
        )
        if code and st.button("Load shared quiz", key="btn_load_shared"):
            quiz_data = import_quiz_code(code.strip())
            if not quiz_data or not quiz_data.get("questions"):
                st.error("That doesn't look like a valid quiz code.")
            else:
                _begin_quiz(
                    concepts=quiz_data.get("concepts", []),
                    questions=quiz_data["questions"],
                    content=quiz_data.get("source_description", "Shared quiz"),
                    imported_quiz_data=quiz_data,
                )


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
                st.session_state.analytics = data["analytics"]
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
    try:
        with st.spinner(f"Preparing study material on '{topic['name']}'..."):
            prompt = build_topic_prompt(topic, language=language)
            content = generate_text(prompt)
    except GenerationError as e:
        st.error(str(e))
        return
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not prepare the topic. {e}")
        return
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

    # Two ways to practice this topic: AI-generated, or a ready-made offline set
    offline_questions = get_bank_questions(selected_topic["name"])
    col_ai, col_offline = st.columns(2)

    with col_ai:
        if st.button("Generate Quiz (AI)", key="btn_curriculum", type="primary"):
            if not _configure_gemini():
                st.error("Please enter your Gemini API key above.")
            else:
                launch_curriculum_topic(
                    selected_path, selected_topic, language, match_level=match_level
                )

    with col_offline:
        if offline_questions:
            if st.button(
                f"Practice offline ({len(offline_questions)} Qs, no AI)",
                key="btn_curriculum_offline",
            ):
                quiz = build_quiz_from_questions(
                    offline_questions, title=selected_topic["name"]
                )
                _begin_quiz(
                    concepts=quiz["concepts"],
                    questions=quiz["questions"],
                    content=selected_topic["name"],
                    path_context={"path": selected_path, "topic": selected_topic["name"]},
                )
        else:
            st.caption("No offline set for this topic yet.")


def _render_manual_tab():
    """Render the manual quiz builder - fully functional with no AI/API key."""
    st.markdown(
        "Build a quiz yourself - **no API key or AI needed**. "
        "A reliable backup when the AI is rate-limited or unavailable."
    )

    st.session_state.setdefault("manual_questions", [])
    st.session_state.setdefault("manual_form_nonce", 0)
    nonce = st.session_state.manual_form_nonce

    # Quick-start: load a ready-made offline question set (no AI needed)
    with st.expander(f"Load a ready-made set ({total_bank_questions()} questions available)", expanded=False):
        st.caption("Instantly load hand-written questions for a popular AI/ML topic - then edit or start right away.")
        bank_topic = st.selectbox("Ready-made set", list_bank_topics(), key="bank_topic_select")
        col_load, col_append = st.columns(2)
        with col_load:
            if st.button("Load set", key="btn_bank_load"):
                st.session_state.manual_questions = get_bank_questions(bank_topic)
                st.session_state.manual_title = bank_topic
                st.rerun()
        with col_append:
            if st.button("Add to current", key="btn_bank_append"):
                st.session_state.manual_questions.extend(get_bank_questions(bank_topic))
                st.rerun()

    title = st.text_input("Quiz title / topic", key="manual_title")

    st.markdown("#### Add a question")
    q_text = st.text_area("Question", key=f"mq_text_{nonce}")
    type_label = st.selectbox(
        "Type",
        ["Multiple choice", "True / False", "Fill in the blank"],
        key=f"mq_type_{nonce}",
    )

    options: list[str] = []
    correct = ""
    if type_label == "Multiple choice":
        c = st.columns(2)
        o1 = c[0].text_input("Option A", key=f"mq_o1_{nonce}")
        o2 = c[1].text_input("Option B", key=f"mq_o2_{nonce}")
        o3 = c[0].text_input("Option C", key=f"mq_o3_{nonce}")
        o4 = c[1].text_input("Option D", key=f"mq_o4_{nonce}")
        options = [o1, o2, o3, o4]
        nonempty = [o for o in options if o.strip()]
        correct = st.selectbox(
            "Correct option",
            nonempty or ["(enter options above)"],
            key=f"mq_correct_mcq_{nonce}",
        )
    elif type_label == "True / False":
        correct = st.radio(
            "Correct answer", ["True", "False"],
            key=f"mq_correct_tf_{nonce}", horizontal=True,
        )
    else:
        correct = st.text_input("Correct answer", key=f"mq_correct_fb_{nonce}")

    concept = st.text_input("Concept (optional)", key=f"mq_concept_{nonce}")
    explanation = st.text_area("Explanation (optional)", key=f"mq_expl_{nonce}")

    if st.button("Add question", key=f"mq_add_{nonce}"):
        type_map = {
            "Multiple choice": "mcq",
            "True / False": "true_false",
            "Fill in the blank": "fill_blank",
        }
        q = {
            "question": q_text,
            "type": type_map[type_label],
            "options": [o for o in options if o.strip()] if type_label == "Multiple choice" else [],
            "correct_answer": correct,
            "concept": concept,
            "explanation": explanation,
        }
        err = validate_question(q)
        if err:
            st.error(err)
        else:
            st.session_state.manual_questions.append(q)
            st.session_state.manual_form_nonce += 1  # reset the input fields
            st.rerun()

    # Current draft questions
    qs = st.session_state.manual_questions
    st.divider()
    if qs:
        st.markdown(f"#### Your questions ({len(qs)})")
        for i, q in enumerate(qs):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"**{i + 1}. {q['question']}**  _({q['type']})_  \n"
                    f"Answer: {q['correct_answer']}"
                )
            with col2:
                if st.button("Remove", key=f"mq_del_{i}"):
                    st.session_state.manual_questions.pop(i)
                    st.rerun()

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Start Quiz", type="primary", key="mq_start"):
                quiz = build_quiz_from_questions(qs, title=title or "My Quiz")
                _begin_quiz(
                    concepts=quiz["concepts"],
                    questions=quiz["questions"],
                    content=title or "Manual quiz",
                )
        with col_b:
            if st.button("Clear all", key="mq_clear"):
                st.session_state.manual_questions = []
                st.rerun()
    else:
        st.caption("Add at least one question above to start your quiz.")


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
    tab_curriculum, tab_manual, tab_pdf, tab_text, tab_topic = st.tabs(
        ["AI/ML Curriculum", "Build Manually", "Upload PDF", "Paste Text", "Enter Topic"]
    )

    with tab_curriculum:
        _render_curriculum_tab(language)

    with tab_manual:
        _render_manual_tab()

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
            try:
                content = parse_pdf(uploaded_file)
            except Exception as e:  # noqa: BLE001 - surface a friendly message
                st.error(f"Could not read this PDF (it may be scanned or encrypted). {e}")
                return
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
            lang_instruction = f" Write in {language}." if language != "English" else ""
            try:
                with st.spinner("Generating study material..."):
                    content = generate_text(
                        f"Write a comprehensive educational summary (500-800 words) about: {topic}. "
                        f"Cover the key concepts, important details, and relationships between ideas. "
                        f"Write in a clear, textbook-like style suitable for studying.{lang_instruction}"
                    )
            except GenerationError as e:
                st.error(str(e))
                return
            except Exception as e:  # noqa: BLE001
                st.error(f"Could not generate study material. {e}")
                return
            _process_content(content)

    # Shared quiz + import sections at bottom
    st.divider()
    _render_shared_quiz_section()
    _render_import_section()
