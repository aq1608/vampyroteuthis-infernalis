"""
Adaptive Quiz Generator - Main Streamlit Application

An AI-powered educational tool that generates personalized quizzes,
adapts difficulty, provides an AI tutor, tracks progress with gamification,
and visualizes learning through knowledge graphs and analytics.

Built for the Prometheus July AI Challenge 2026.
"""

from __future__ import annotations

import os
import streamlit as st
from dotenv import load_dotenv

from ui.styles import inject_css, inject_dark_mode_css
from ui.accessibility import render_accessibility_settings, inject_accessibility_css
from ui.onboarding import should_show_onboarding, render_onboarding
from ui.upload_page import render_upload_page
from ui.quiz_page import render_quiz_page
from ui.results_page import render_results_page
from ui.tutor_page import render_tutor_page
from ui.analytics_page import render_analytics_page
from ui.graph_page import render_graph_page
from quiz_engine.gamification import GamificationEngine
from quiz_engine.spaced_repetition import SpacedRepetitionEngine
from quiz_engine.analytics import AnalyticsEngine

# Load environment variables from a local .env file (for local development)
load_dotenv()


def _bridge_secrets_to_env():
    """
    Copy configured secrets into os.environ.

    On Streamlit Community Cloud these come from st.secrets; the quiz_engine
    modules read them with os.getenv(...), so we copy them into the environment
    once at startup. Each lookup is wrapped in try/except because st.secrets
    raises if no secrets file/config exists locally.

    - GEMINI_API_KEY: required for AI features (or pasted in the UI).
    - SUPABASE_URL / SUPABASE_KEY: optional, enable the live shared leaderboard.
    """
    for key in ("GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"):
        if os.getenv(key):
            continue
        try:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
        except Exception:
            # No secrets configured; features degrade gracefully.
            pass


_bridge_secrets_to_env()

# Page configuration
st.set_page_config(
    page_title="Adaptive Quiz Generator",
    page_icon="\U0001F9E0",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inject custom CSS
inject_css()



def init_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        # Navigation
        "page": "upload",
        # Quiz state
        "content": None,
        "concepts": [],
        "questions": [],
        "current_question_idx": 0,
        "answers": [],
        "adaptive_engine": None,
        "quiz_complete": False,
        # Set True once a quiz's results have been recorded, so the scoring
        # side effects run exactly once (not on every results-page rerun).
        "results_recorded": False,
        # Guided curriculum path
        "path_context": None,          # {"path": name, "topic": name} for current quiz
        "completed_topics": {},        # path_name -> list of completed topic names
        # Settings
        "language": "English",
        "timer_enabled": False,
        "timer_seconds": 30,
        "dark_mode": False,
        # Gamification
        "gamification": GamificationEngine(),
        # Spaced repetition
        "spaced_rep": SpacedRepetitionEngine(),
        # Analytics
        "analytics": AnalyticsEngine(),
        # Quiz history
        "quiz_history": [],
        # Onboarding
        "onboarding_complete": False,
        "onboarding_step": 0,
        # Tutor
        "tutor_messages": [],
        # Collaborative
        "player_name": "Player",
        "imported_quiz_data": None,   # Shared quiz being played (carries leaderboard)
        "quiz_start_time": None,      # For leaderboard time tracking
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render the sidebar with gamification, settings, and navigation."""
    with st.sidebar:
        gam = st.session_state.gamification
        level = gam.current_level

        # Level and XP
        st.markdown(f"### {level['title']} (Lvl {level['level']})")
        next_lvl = gam.next_level
        if next_lvl:
            xp_in = gam.total_xp - level["xp_required"]
            xp_needed = next_lvl["xp_required"] - level["xp_required"]
            st.progress(gam.xp_progress)
            st.caption(f"{xp_in}/{xp_needed} XP to Level {next_lvl['level']}")
        else:
            st.progress(1.0)
            st.caption("MAX LEVEL!")

        st.markdown(f"**Total XP:** {gam.total_xp}")
        st.markdown(f"**Best Streak:** {gam.best_streak}")
        st.markdown(f"**Quizzes:** {gam.quizzes_completed}")

        # Badges
        earned = [gam.get_badge_info(b) for b in gam.badges_earned]
        if earned:
            badge_text = " ".join(f"{b['emoji']}" for b in earned)
            st.markdown(badge_text)

        # Navigation
        st.divider()
        st.markdown("### Navigate")

        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
        if st.button("AI Tutor", key="nav_tutor", use_container_width=True):
            st.session_state.page = "tutor"
            st.rerun()
        if st.button("Knowledge Graph", key="nav_graph", use_container_width=True):
            st.session_state.page = "graph"
            st.rerun()
        if st.button("Analytics", key="nav_analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()

        # Settings
        st.divider()
        st.markdown("### Settings")

        languages = [
            "English", "Spanish", "French", "German", "Portuguese",
            "Italian", "Japanese", "Korean", "Chinese", "Hindi",
            "Arabic", "Russian",
        ]
        # Reflect the current language (e.g. after importing progress) instead
        # of always defaulting the dropdown back to English on first render.
        current_language = st.session_state.get("language", "English")
        if current_language not in languages:
            current_language = "English"
        st.session_state.language = st.selectbox(
            "Quiz Language",
            languages,
            index=languages.index(current_language),
            key="lang_select",
        )

        st.session_state.dark_mode = st.toggle(
            "Dark Mode",
            value=st.session_state.get("dark_mode", False),
            key="dark_mode_toggle",
        )

        st.session_state.timer_enabled = st.toggle(
            "Timer Mode",
            value=st.session_state.get("timer_enabled", False),
            key="timer_toggle",
        )
        if st.session_state.timer_enabled:
            st.session_state.timer_seconds = st.slider(
                "Seconds per question",
                min_value=10, max_value=120, value=30, step=5,
                key="timer_slider",
            )

        st.session_state.player_name = st.text_input(
            "Your Name (for sharing)",
            value=st.session_state.get("player_name", "Player"),
            key="player_name_input",
        )

        # Accessibility
        st.divider()
        render_accessibility_settings()


def main():
    """Main application entry point."""
    init_session_state()

    # Show onboarding for first-time users
    if should_show_onboarding():
        render_onboarding()
        return

    # Render sidebar first so its toggles update session state, THEN inject the
    # theme/accessibility CSS from those fresh values. (Injecting before the
    # sidebar made every toggle take effect only on the next rerun.)
    render_sidebar()
    inject_dark_mode_css()
    inject_accessibility_css()

    # Route to the correct page
    page = st.session_state.page
    if page == "upload":
        render_upload_page()
    elif page == "quiz":
        render_quiz_page()
    elif page == "results":
        render_results_page()
    elif page == "tutor":
        render_tutor_page()
    elif page == "analytics":
        render_analytics_page()
    elif page == "graph":
        render_graph_page()


if __name__ == "__main__":
    main()
