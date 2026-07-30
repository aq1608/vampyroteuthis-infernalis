"""
AI Tutor Chat Page - Conversational learning assistant.

Provides a chat interface where students can ask follow-up questions
about concepts they're studying. The tutor adapts its explanations
based on quiz performance.
"""

from __future__ import annotations

import streamlit as st

from quiz_engine.ai_tutor import (
    chat_with_tutor,
    create_tutor_context,
)


def _reply_to_pending_user_message(engine):
    """Generate and append a tutor reply if the last message is from the user."""
    messages = st.session_state.tutor_messages
    if not messages or messages[-1]["role"] != "user":
        return

    concept_states = engine.concept_states if engine else {}
    system_context = create_tutor_context(
        content=st.session_state.get("content", ""),
        concept_states=concept_states,
        language=st.session_state.get("language", "English"),
    )

    with st.spinner("Thinking..."):
        response = chat_with_tutor(
            messages=messages,
            system_context=system_context,
        )

    st.session_state.tutor_messages.append({
        "role": "assistant",
        "content": response,
    })
    st.rerun()


def render_tutor_page():
    """Render the AI tutor chat interface."""

    st.markdown("### AI Tutor")
    st.caption(
        "Ask me anything about the concepts you're studying. "
        "I'll adapt my explanations to your level."
    )

    # Initialize chat history
    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = []

    # Quick concept buttons if we have concept data
    engine = st.session_state.get("adaptive_engine")
    if engine and engine.concept_states:
        weak_concepts = [
            c for c in engine.concept_states.values()
            if c.mastery_score < 0.7
        ]
        if weak_concepts:
            st.markdown("**Quick help with:**")
            cols = st.columns(min(len(weak_concepts), 4))
            for i, concept in enumerate(weak_concepts[:4]):
                with cols[i]:
                    if st.button(
                        f"{concept.name}",
                        key=f"concept_btn_{i}",
                    ):
                        st.session_state.tutor_messages.append({
                            "role": "user",
                            "content": f"Can you explain {concept.name} to me in a simple way?",
                        })
                        st.rerun()

    st.divider()

    # Chat messages display
    for msg in st.session_state.tutor_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask the tutor a question...")

    if user_input:
        st.session_state.tutor_messages.append({
            "role": "user",
            "content": user_input,
        })
        st.rerun()

    # Generate a reply whenever the latest message is an unanswered user turn.
    # This covers BOTH the chat input above and the quick-help concept buttons
    # (which previously added a question that never got a response).
    _reply_to_pending_user_message(engine)

    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Results"):
            st.session_state.page = "results"
            st.rerun()
    with col2:
        if st.button("Clear Chat"):
            st.session_state.tutor_messages = []
            st.rerun()
