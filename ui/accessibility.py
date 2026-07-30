"""
Accessibility features - Make the app usable for everyone.

Provides:
- High contrast mode
- Dyslexia-friendly font (OpenDyslexic)
- Large text mode
- Reduced animations
"""

from __future__ import annotations

import streamlit as st


ACCESSIBILITY_CSS = """
<style>
/* ===== High Contrast Mode ===== */
.high-contrast {{
    --bg-primary: #000000 !important;
    --text-primary: #FFFFFF !important;
    --bg-card: #1A1A1A !important;
    --border-color: #FFFFFF !important;
}}

.high-contrast .stApp {{
    background-color: #000000 !important;
    color: #FFFFFF !important;
}}

.high-contrast .stMarkdown, .high-contrast p, .high-contrast span {{
    color: #FFFFFF !important;
}}

.high-contrast .stButton > button {{
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #FFFFFF !important;
}}

/* ===== Dyslexia-Friendly Font ===== */
.dyslexia-font * {{
    font-family: 'OpenDyslexic', 'Comic Sans MS', sans-serif !important;
    letter-spacing: 0.05em !important;
    word-spacing: 0.1em !important;
    line-height: 1.8 !important;
}}

/* ===== Large Text Mode ===== */
.large-text .stMarkdown p,
.large-text .stMarkdown li {{
    font-size: 1.2rem !important;
}}

.large-text .stRadio label {{
    font-size: 1.1rem !important;
}}

.large-text .stTextInput input {{
    font-size: 1.1rem !important;
}}

/* ===== Reduced Animations ===== */
.reduced-motion * {{
    animation: none !important;
    transition: none !important;
}}
</style>

{font_import}
"""

DYSLEXIC_FONT_IMPORT = """
<style>
@import url('https://fonts.cdnfonts.com/css/opendyslexic');
</style>
"""


def render_accessibility_settings():
    """Render accessibility settings in the sidebar."""
    st.markdown("### Accessibility")

    high_contrast = st.toggle(
        "High Contrast",
        value=st.session_state.get("a11y_high_contrast", False),
        key="a11y_contrast_toggle",
        help="Black background with white text for better visibility",
    )
    st.session_state.a11y_high_contrast = high_contrast

    dyslexia_font = st.toggle(
        "Dyslexia-Friendly Font",
        value=st.session_state.get("a11y_dyslexia_font", False),
        key="a11y_dyslexia_toggle",
        help="Use OpenDyslexic font with increased spacing",
    )
    st.session_state.a11y_dyslexia_font = dyslexia_font

    large_text = st.toggle(
        "Large Text",
        value=st.session_state.get("a11y_large_text", False),
        key="a11y_large_toggle",
        help="Increase text size throughout the app",
    )
    st.session_state.a11y_large_text = large_text

    reduced_motion = st.toggle(
        "Reduce Animations",
        value=st.session_state.get("a11y_reduced_motion", False),
        key="a11y_motion_toggle",
        help="Disable all animations for motion sensitivity",
    )
    st.session_state.a11y_reduced_motion = reduced_motion


def inject_accessibility_css():
    """Inject accessibility CSS based on current settings."""
    classes = []

    if st.session_state.get("a11y_high_contrast"):
        classes.append("high-contrast")
    if st.session_state.get("a11y_dyslexia_font"):
        classes.append("dyslexia-font")
    if st.session_state.get("a11y_large_text"):
        classes.append("large-text")
    if st.session_state.get("a11y_reduced_motion"):
        classes.append("reduced-motion")

    font_import = ""
    if st.session_state.get("a11y_dyslexia_font"):
        font_import = DYSLEXIC_FONT_IMPORT

    css = ACCESSIBILITY_CSS.format(font_import=font_import)
    st.markdown(css, unsafe_allow_html=True)

    # Apply classes to body via JS
    if classes:
        class_str = " ".join(classes)
        st.markdown(
            f"""<script>
            document.querySelector('.stApp').className += ' {class_str}';
            </script>""",
            unsafe_allow_html=True,
        )
