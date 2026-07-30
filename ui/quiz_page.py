"""
Quiz Page - Interactive quiz with timer, gamification, and adaptive feedback.

Features:
- Real-time difficulty adaptation
- Optional countdown timer per question
- XP awards and streak tracking
- Visual feedback with animations
"""

from __future__ import annotations

import time
import streamlit as st

from quiz_engine.evaluator import evaluate_answer
from ui.styles import render_difficulty_badge


# Prefixes of the per-question session keys created while taking a quiz. These
# are indexed by question number and MUST be cleared when a new quiz starts,
# otherwise stale "already answered" flags make the next quiz skip its early
# questions (recording only the last one).
_QUIZ_WIDGET_PREFIXES = ("feedback_shown_", "answer_", "timer_start_", "time_up_")


def clear_quiz_widget_state():
    """Remove per-question widget/flag keys left over from a previous quiz."""
    stale = [
        k for k in list(st.session_state.keys())
        if k.startswith(_QUIZ_WIDGET_PREFIXES)
    ]
    for k in stale:
        del st.session_state[k]


def _render_question(question: dict):
    """Render a single question based on its type."""
    st.markdown(f"**{question['question']}**")

    q_type = question.get("type", "mcq")

    if q_type == "mcq":
        answer = st.radio(
            "Choose your answer:",
            options=question.get("options", []),
            key=f"answer_{st.session_state.current_question_idx}",
            index=None,
        )
    elif q_type == "true_false":
        answer = st.radio(
            "Choose your answer:",
            options=["True", "False"],
            key=f"answer_{st.session_state.current_question_idx}",
            index=None,
        )
    elif q_type == "fill_blank":
        answer = st.text_input(
            "Your answer:",
            key=f"answer_{st.session_state.current_question_idx}",
        )
    else:
        answer = st.text_input(
            "Your answer:",
            key=f"answer_{st.session_state.current_question_idx}",
        )

    return answer



def _handle_submission(question: dict, answer: str, within_time: bool = True):
    """Process the submitted answer and update adaptive engine + gamification."""
    # Evaluate the answer
    result = evaluate_answer(question, answer)
    is_correct = result["is_correct"]

    # Record in adaptive engine
    concept_name = question.get("concept", "General")
    engine = st.session_state.adaptive_engine
    adaptation = engine.record_answer(concept_name, is_correct)

    # Award XP via gamification
    gam = st.session_state.gamification
    difficulty = question.get("difficulty", "beginner")
    xp_earned = gam.award_xp(difficulty, is_correct)

    # Track timer mode
    if st.session_state.timer_enabled and within_time and is_correct:
        gam.record_timed_answer()

    # Store in answers history
    st.session_state.answers.append({
        "question": question,
        "student_answer": answer,
        "is_correct": is_correct,
        "adaptation": adaptation,
        "xp_earned": xp_earned,
    })

    return is_correct, adaptation, xp_earned


@st.fragment(run_every=1)
def _render_timer(idx: int, total_seconds: int):
    """
    Live countdown for the current question, refreshed once per second.

    Runs as a fragment so only the timer re-renders each tick (not the whole
    page). When it hits zero it flags the question as timed-out and triggers a
    full app rerun, which lets render_quiz_page auto-submit the answer.
    """
    # Freeze once the question has been answered.
    if st.session_state.get(f"feedback_shown_{idx}"):
        return

    start = st.session_state.get(f"timer_start_{idx}")
    if start is None:
        start = time.time()
        st.session_state[f"timer_start_{idx}"] = start

    remaining = max(0, total_seconds - int(time.time() - start))

    if remaining <= 0:
        st.session_state[f"time_up_{idx}"] = True
        st.rerun(scope="app")
        return

    if remaining <= 5:
        st.markdown(
            f'<div class="timer-container">'
            f'<span class="timer-value timer-warning">{remaining}s</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.progress(remaining / total_seconds)
        st.caption(f"Time remaining: {remaining}s")


def _render_gamification_status():
    """Render current streak and level info."""
    gam = st.session_state.gamification
    cols = st.columns([1, 1, 1])

    with cols[0]:
        if gam.current_streak > 0:
            st.markdown(
                f'<div class="streak-container">'
                f'Streak: {gam.current_streak}</div>',
                unsafe_allow_html=True,
            )

    with cols[1]:
        level = gam.current_level
        st.caption(f"Level {level['level']} {level['title']}")

    with cols[2]:
        st.caption(f"{gam.total_xp} XP")



def render_quiz_page():
    """Render the interactive quiz page."""
    questions = st.session_state.questions
    current_idx = st.session_state.current_question_idx
    engine = st.session_state.adaptive_engine

    if not questions:
        st.error("No questions available. Please go back and upload content.")
        if st.button("Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # Check if quiz is over
    total_questions = len(questions)
    if current_idx >= total_questions:
        st.session_state.quiz_complete = True
        st.session_state.page = "results"
        st.rerun()
        return

    # Gamification status bar
    _render_gamification_status()

    st.divider()

    # Progress indicator
    progress = current_idx / total_questions
    st.progress(progress)

    current_question = questions[current_idx]
    concept_name = current_question.get("concept", "General")
    difficulty = engine.get_current_difficulty(concept_name)

    # Question header
    col_q, col_d = st.columns([3, 1])
    with col_q:
        st.markdown(f"**Question {current_idx + 1} of {total_questions}**")
        st.caption(f"Concept: {concept_name}")
    with col_d:
        st.markdown(
            render_difficulty_badge(difficulty),
            unsafe_allow_html=True,
        )

    feedback_key = f"feedback_shown_{current_idx}"
    timer_enabled = st.session_state.timer_enabled
    time_up = timer_enabled and st.session_state.get(f"time_up_{current_idx}", False)

    # Timer: live countdown only while the question is still unanswered and time
    # has not already expired (once expired we fall straight through to the
    # auto-submit below instead of re-rendering the ticking fragment).
    if timer_enabled and not st.session_state.get(feedback_key) and not time_up:
        _render_timer(current_idx, st.session_state.timer_seconds)

    st.divider()

    # Render the question
    answer = _render_question(current_question)

    # Submit / auto-submit
    if not st.session_state.get(feedback_key):
        if time_up:
            # Time expired: auto-submit whatever is currently selected (may be
            # empty, which evaluates as incorrect). No speed bonus.
            current_answer = st.session_state.get(f"answer_{current_idx}") or ""
            _handle_submission(current_question, current_answer, within_time=False)
            st.warning("Time's up! Moving on.")
            st.session_state[feedback_key] = True
            st.rerun()

        elif st.button("Submit Answer", type="primary",
                       disabled=(answer is None or answer == "")):
            is_correct, adaptation, xp_earned = _handle_submission(
                current_question, answer, within_time=True
            )

            if is_correct:
                msg = f"Correct! +{xp_earned} XP"
                if adaptation["action"] == "level_up":
                    msg += f" | Level Up! Now at {adaptation['new_difficulty']}!"
                    st.balloons()
                st.success(msg)
            else:
                st.error(
                    f"Incorrect. The correct answer is: "
                    f"**{current_question['correct_answer']}**"
                )
                # Show explanation
                if current_question.get("explanation"):
                    st.info(f"{current_question['explanation']}")
                if adaptation["action"] == "explain_and_retry":
                    st.warning(f"{adaptation['message']}")
                elif adaptation["action"] == "flag_review":
                    st.warning(f"{adaptation['message']}")

            st.session_state[feedback_key] = True
            st.rerun()

    # Navigation after feedback
    if st.session_state.get(feedback_key):
        # Show what happened
        last_answer = st.session_state.answers[-1] if st.session_state.answers else None
        if last_answer and last_answer["question"] == current_question:
            if last_answer["is_correct"]:
                st.success(
                    f"Correct! +{last_answer['xp_earned']} XP"
                )
            else:
                st.error(
                    f"Incorrect. Correct answer: "
                    f"**{current_question['correct_answer']}**"
                )
                if current_question.get("explanation"):
                    st.info(f"{current_question['explanation']}")

        # Next button
        if current_idx + 1 < total_questions:
            if st.button("Next Question", type="primary"):
                st.session_state.current_question_idx += 1
                st.rerun()
        else:
            if st.button("See Results", type="primary"):
                st.session_state.quiz_complete = True
                st.session_state.page = "results"
                st.rerun()

    # End early option
    st.divider()
    if st.button("End Quiz Early"):
        st.session_state.quiz_complete = True
        st.session_state.page = "results"
        st.rerun()
