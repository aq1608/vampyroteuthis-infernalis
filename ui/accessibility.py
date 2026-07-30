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


# Each block targets Streamlit's real DOM containers directly, so it applies as
# soon as it is injected - no body class and no JavaScript required. (Streamlit
# strips <script> tags from st.markdown, so the previous JS-based class toggle
# never actually took effect.)
_APP = '[data-testid="stAppViewContainer"]'
_SIDEBAR = '[data-testid="stSidebar"]'

HIGH_CONTRAST_CSS = f"""
{_APP}, {_SIDEBAR}, [data-testid="stHeader"] {{
    background-color: #000000 !important;
}}
{_APP} *, {_SIDEBAR} * {{
    color: #FFFFFF !important;
    border-color: #FFFFFF !important;
}}
{_APP} .stButton > button, {_SIDEBAR} .stButton > button {{
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #FFFFFF !important;
}}
"""

# The @import is emitted in its own <style> tag (a CSS @import is only honored
# at the very top of a stylesheet, and this block may be concatenated after
# others), so keep the font-family rules separate from the import itself.
DYSLEXIA_FONT_IMPORT = (
    "<style>@import url('https://fonts.cdnfonts.com/css/opendyslexic');</style>"
)

DYSLEXIA_FONT_CSS = f"""
{_APP} *, {_SIDEBAR} * {{
    font-family: 'OpenDyslexic', 'Comic Sans MS', sans-serif !important;
    letter-spacing: 0.05em !important;
    word-spacing: 0.1em !important;
    line-height: 1.8 !important;
}}
"""

LARGE_TEXT_CSS = f"""
{_APP} .stMarkdown p, {_APP} .stMarkdown li,
{_SIDEBAR} .stMarkdown p, {_SIDEBAR} .stMarkdown li {{
    font-size: 1.2rem !important;
}}
{_APP} .stRadio label, {_SIDEBAR} .stRadio label {{
    font-size: 1.1rem !important;
}}
{_APP} .stTextInput input, {_APP} .stTextArea textarea {{
    font-size: 1.1rem !important;
}}
"""

REDUCED_MOTION_CSS = f"""
{_APP} *, {_SIDEBAR} * {{
    animation: none !important;
    transition: none !important;
}}
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
    """
    Inject accessibility CSS based on the current sidebar settings.

    Only the enabled blocks are emitted, each already scoped to Streamlit's real
    containers, so the styles take effect immediately with no JavaScript.
    """
    blocks = []

    if st.session_state.get("a11y_high_contrast"):
        blocks.append(HIGH_CONTRAST_CSS)
    if st.session_state.get("a11y_dyslexia_font"):
        # Font @import first, in its own tag, so it is always honored.
        st.markdown(DYSLEXIA_FONT_IMPORT, unsafe_allow_html=True)
        blocks.append(DYSLEXIA_FONT_CSS)
    if st.session_state.get("a11y_large_text"):
        blocks.append(LARGE_TEXT_CSS)
    if st.session_state.get("a11y_reduced_motion"):
        blocks.append(REDUCED_MOTION_CSS)

    if not blocks:
        return

    st.markdown(
        "<style>\n" + "\n".join(blocks) + "\n</style>",
        unsafe_allow_html=True,
    )
