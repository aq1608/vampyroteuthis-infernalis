"""
Custom CSS styles for the Adaptive Quiz Generator.

Provides branded styling, animations, and polished UI components.
"""

from __future__ import annotations


CUSTOM_CSS = """
<style>
/* ===== Global Theme ===== */
:root {
    --primary: #6C63FF;
    --primary-dark: #5A52E0;
    --success: #2ECC71;
    --warning: #F39C12;
    --danger: #E74C3C;
    --bg-card: #F8F9FA;
    --text-primary: #2C3E50;
    --text-secondary: #7F8C8D;
    --border-radius: 12px;
}

/* ===== Hero Section ===== */
.hero-container {
    text-align: center;
    padding: 2rem 1rem;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    font-size: 1.2rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-top: 0;
}

/* ===== Feature Cards ===== */
.feature-card {
    background: var(--bg-card);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    margin: 0.5rem 0;
    border: 1px solid #E8E8E8;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(108, 99, 255, 0.15);
}

.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.feature-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0.25rem 0;
}

.feature-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
}

/* ===== Difficulty Badges ===== */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-beginner {
    background: #D5F5E3;
    color: #1E8449;
}

.badge-intermediate {
    background: #FEF9E7;
    color: #B7950B;
}

.badge-advanced {
    background: #FDEDEC;
    color: #922B21;
}

/* ===== Quiz Card ===== */
.quiz-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 2rem;
    border: 2px solid #E8E8E8;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.question-number {
    font-size: 0.85rem;
    color: var(--primary);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

/* ===== Results Cards ===== */
.score-card {
    background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%);
    border-radius: var(--border-radius);
    padding: 2rem;
    text-align: center;
    color: white;
    margin: 1rem 0;
}

.score-value {
    font-size: 3rem;
    font-weight: 800;
    margin: 0.5rem 0;
}

.score-label {
    font-size: 0.9rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ===== Concept Mastery Bar ===== */
.mastery-bar {
    background: #ECECEC;
    border-radius: 10px;
    height: 12px;
    overflow: hidden;
    margin: 0.25rem 0;
}

.mastery-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}

.mastery-fill-high {
    background: linear-gradient(90deg, #2ECC71, #27AE60);
}

.mastery-fill-medium {
    background: linear-gradient(90deg, #F39C12, #E67E22);
}

.mastery-fill-low {
    background: linear-gradient(90deg, #E74C3C, #C0392B);
}

/* ===== Gamification ===== */
.xp-bar {
    background: #ECECEC;
    border-radius: 20px;
    height: 20px;
    overflow: hidden;
    position: relative;
    margin: 0.5rem 0;
}

.xp-fill {
    background: linear-gradient(90deg, #6C63FF, #4ECDC4);
    height: 100%;
    border-radius: 20px;
    transition: width 0.8s ease;
}

.xp-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.75rem;
    font-weight: 700;
    color: #333;
}

.badge-earned {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #FEF9E7;
    border: 2px solid #F1C40F;
    border-radius: 20px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.25rem;
    animation: badgePop 0.3s ease;
}

@keyframes badgePop {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); opacity: 1; }
}

/* ===== Streak Counter ===== */
.streak-container {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, #FF6B6B, #FF8E53);
    border-radius: 20px;
    padding: 0.4rem 1rem;
    color: white;
    font-weight: 700;
    font-size: 0.9rem;
}

/* ===== Timer ===== */
.timer-container {
    text-align: center;
    margin: 0.5rem 0;
}

.timer-value {
    font-size: 1.5rem;
    font-weight: 700;
    font-family: 'Courier New', monospace;
}

.timer-warning {
    color: var(--danger);
    animation: timerPulse 1s infinite;
}

@keyframes timerPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ===== Animations ===== */
@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: slideIn 0.4s ease forwards;
}

@keyframes correctPulse {
    0% { background-color: transparent; }
    50% { background-color: rgba(46, 204, 113, 0.1); }
    100% { background-color: transparent; }
}

.correct-flash {
    animation: correctPulse 0.6s ease;
}

/* ===== Stats Grid ===== */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.stat-item {
    background: var(--bg-card);
    border-radius: var(--border-radius);
    padding: 1rem;
    text-align: center;
    border: 1px solid #E8E8E8;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--primary);
}

.stat-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ===== Streamlit Overrides ===== */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF 0%, #5A52E0 100%);
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
}

.stProgress > div > div {
    background: linear-gradient(90deg, #6C63FF, #4ECDC4);
    border-radius: 10px;
}

/* Hide Streamlit default elements for cleaner look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero():
    """Render the hero section on the landing page."""
    import streamlit as st
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Adaptive Quiz Generator</div>
        <p class="hero-subtitle">Upload any content. Get a personalized quiz that adapts to you.</p>
    </div>
    """, unsafe_allow_html=True)


def render_feature_cards():
    """Render feature highlight cards on the landing page."""
    import streamlit as st

    cols = st.columns(3)
    features = [
        ("brain", "AI-Powered", "Questions generated by AI, tailored to your content"),
        ("chart_with_upwards_trend", "Adaptive", "Difficulty adjusts based on your performance"),
        ("bulb", "Instant Feedback", "Get explanations when you make mistakes"),
    ]

    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def render_difficulty_badge(difficulty: str) -> str:
    """Return HTML for a difficulty badge."""
    badge_class = f"badge-{difficulty}"
    return f'<span class="badge {badge_class}">{difficulty}</span>'


def render_score_card(score: int, total: int, percentage: float) -> str:
    """Return HTML for the main score card."""
    return f"""
    <div class="score-card">
        <div class="score-label">Your Score</div>
        <div class="score-value">{score}/{total}</div>
        <div class="score-label">{percentage:.0f}% Correct</div>
    </div>
    """


def render_mastery_bar(mastery: float, concept_name: str) -> str:
    """Return HTML for a concept mastery progress bar."""
    percentage = mastery * 100
    if mastery >= 0.8:
        fill_class = "mastery-fill-high"
    elif mastery >= 0.5:
        fill_class = "mastery-fill-medium"
    else:
        fill_class = "mastery-fill-low"

    return f"""
    <div style="margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 600; font-size: 0.9rem;">{concept_name}</span>
            <span style="font-size: 0.8rem; color: #7F8C8D;">{percentage:.0f}%</span>
        </div>
        <div class="mastery-bar">
            <div class="mastery-fill {fill_class}" style="width: {percentage}%;"></div>
        </div>
    </div>
    """
