"""
Onboarding Flow - Guided first-time user experience.

Shows a welcoming walkthrough that demonstrates the app's features
and offers a sample quiz to try immediately.
"""

from __future__ import annotations

import streamlit as st



SAMPLE_QUESTIONS = [
    {
        "question": "What is the main benefit of active recall in learning?",
        "type": "mcq",
        "options": [
            "It makes reading faster",
            "It forces your brain to retrieve information, strengthening memory",
            "It reduces the amount you need to study",
            "It only works for visual learners",
        ],
        "correct_answer": "It forces your brain to retrieve information, strengthening memory",
        "concept": "Active Recall",
        "difficulty": "beginner",
        "explanation": "Active recall works by making your brain actively retrieve information rather than passively re-reading it. This strengthens neural pathways and improves long-term retention.",
    },
    {
        "question": "Spaced repetition means reviewing material at increasing intervals over time.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Spaced Repetition",
        "difficulty": "beginner",
        "explanation": "Spaced repetition schedules reviews at optimal intervals - just before you're about to forget - which maximizes long-term memory formation.",
    },
    {
        "question": "According to research, students retain approximately what percentage of material after passive reading?",
        "type": "mcq",
        "options": ["10-20%", "40-50%", "70-80%", "90-100%"],
        "correct_answer": "10-20%",
        "concept": "Learning Science",
        "difficulty": "intermediate",
        "explanation": "Research shows passive reading has very low retention rates. Active methods like self-testing can increase retention to 60-80%.",
    },
]

SAMPLE_CONCEPTS = [
    {"name": "Active Recall", "description": "Testing yourself to strengthen memory", "importance": "high"},
    {"name": "Spaced Repetition", "description": "Reviewing at optimal intervals", "importance": "high"},
    {"name": "Learning Science", "description": "Research-backed study methods", "importance": "medium"},
]


def should_show_onboarding() -> bool:
    """Check if we should show the onboarding flow."""
    return not st.session_state.get("onboarding_complete", False)


def render_onboarding():
    """Render the onboarding experience."""
    step = st.session_state.get("onboarding_step", 0)

    if step == 0:
        _render_welcome()
    elif step == 1:
        _render_features()
    elif step == 2:
        _render_how_it_works()
    elif step == 3:
        _render_try_it()
    else:
        st.session_state.onboarding_complete = True
        st.session_state.page = "upload"
        st.rerun()


def _render_welcome():
    """Step 1: Welcome screen."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #6C63FF, #4ECDC4); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Welcome to Adaptive Quiz Generator
        </h1>
        <p style="font-size: 1.2rem; color: #7F8C8D; margin-top: 1rem;">
            Your AI-powered study companion that makes learning active, personalized, and fun.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Upload anything**")
        st.caption("PDFs, text, or just a topic name")
    with col2:
        st.markdown("**AI generates quizzes**")
        st.caption("Personalized to your content")
    with col3:
        st.markdown("**Learn faster**")
        st.caption("Adaptive difficulty + instant feedback")

    st.markdown("")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Get Started", type="primary"):
            st.session_state.onboarding_step = 1
            st.rerun()
    with col1:
        if st.button("Skip Tour"):
            st.session_state.onboarding_complete = True
            st.session_state.page = "upload"
            st.rerun()


def _render_features():
    """Step 2: Feature highlights."""
    st.markdown("### What can this app do?")
    st.markdown("")

    features = [
        ("Adaptive Difficulty", "Questions get harder when you're doing well, easier when you need help"),
        ("AI Tutor Chat", "Ask follow-up questions and get personalized explanations"),
        ("Knowledge Graph", "See how concepts connect to each other"),
        ("Gamification", "Earn XP, unlock badges, track streaks"),
        ("Spaced Repetition", "AI schedules optimal review times for long-term memory"),
        ("12 Languages", "Generate quizzes in English, Spanish, French, and more"),
        ("Timer Mode", "Practice under exam conditions"),
        ("Study Guides", "AI generates focused study material for your weak areas"),
    ]

    for i in range(0, len(features), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(features):
                name, desc = features[i + j]
                with col:
                    st.markdown(f"**{name}**")
                    st.caption(desc)

    st.markdown("")
    if st.button("Next", type="primary"):
        st.session_state.onboarding_step = 2
        st.rerun()


def _render_how_it_works():
    """Step 3: How it works."""
    st.markdown("### How it works")
    st.markdown("")

    steps = [
        ("1. Upload", "Paste text, upload a PDF, or enter any topic"),
        ("2. AI Extracts", "Key concepts are identified automatically"),
        ("3. Quiz Generated", "Personalized questions at your level"),
        ("4. Adapt & Learn", "Difficulty adjusts based on your answers"),
        ("5. Review & Grow", "Track progress, review weak areas, level up"),
    ]

    for title, desc in steps:
        st.markdown(f"**{title}** — {desc}")

    st.markdown("")
    if st.button("Try a sample quiz!", type="primary"):
        st.session_state.onboarding_step = 3
        st.rerun()


def _render_try_it():
    """Step 4: Offer to start with sample or go to upload."""
    st.markdown("### Ready to start?")
    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Try a sample quiz**")
        st.caption("3 questions about learning science - no API key needed!")
        if st.button("Start Sample Quiz", type="primary"):
            _start_sample_quiz()

    with col2:
        st.markdown("**Upload your own content**")
        st.caption("Bring your own study material")
        if st.button("Go to Upload"):
            st.session_state.onboarding_complete = True
            st.session_state.page = "upload"
            st.rerun()


def _start_sample_quiz():
    """Start the sample quiz without needing an API key."""
    from quiz_engine.adaptive_logic import AdaptiveEngine
    from ui.quiz_page import clear_quiz_widget_state

    clear_quiz_widget_state()

    engine = AdaptiveEngine()
    engine.register_concepts(SAMPLE_CONCEPTS)

    st.session_state.adaptive_engine = engine
    st.session_state.concepts = SAMPLE_CONCEPTS
    st.session_state.questions = SAMPLE_QUESTIONS
    st.session_state.content = "Learning science and study techniques"
    st.session_state.current_question_idx = 0
    st.session_state.answers = []
    st.session_state.quiz_complete = False
    st.session_state.path_context = None
    st.session_state.imported_quiz_data = None
    st.session_state.results_recorded = False
    st.session_state.badges_at_quiz_start = list(
        st.session_state.gamification.badges_earned
    )
    st.session_state.onboarding_complete = True
    st.session_state.page = "quiz"
    st.rerun()
