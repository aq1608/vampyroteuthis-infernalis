"""
AI Tutor - Conversational follow-up when stuck on a concept.

Provides a chat interface where students can ask questions about
concepts they're struggling with. The tutor adapts its explanations
based on the student's quiz performance and learning level.
"""

from __future__ import annotations

import os
from google import genai

from quiz_engine.llm import get_model


TUTOR_SYSTEM_PROMPT = """You are a friendly, patient AI tutor helping a student understand concepts
they are studying. You adapt your explanations to the student's level.

Context about the student:
- They are studying: {topic}
- Their current mastery levels: {mastery_info}
- Concepts they struggled with: {weak_concepts}
- Language preference: {language}

Guidelines:
- Be encouraging and supportive
- Use analogies and real-world examples
- Break complex ideas into simple steps
- Ask follow-up questions to check understanding
- If they seem confused, try a completely different approach to explaining
- Keep responses concise (2-4 paragraphs max) unless they ask for more detail
- Use simple language appropriate to their level
- If asked about something unrelated to the topic, gently redirect

{language_instruction}"""


def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()



def create_tutor_context(
    content: str,
    concept_states: dict,
    language: str = "English",
) -> str:
    """
    Create the system prompt context for the tutor.

    Args:
        content: Original study content.
        concept_states: Dict of concept states from AdaptiveEngine.
        language: Language preference.

    Returns:
        Formatted system prompt string.
    """
    # Build mastery info
    mastery_info = []
    weak_concepts = []
    for name, state in concept_states.items():
        mastery_info.append(
            f"{name}: {state.mastery_score*100:.0f}% mastery"
        )
        if state.mastery_score < 0.7:
            weak_concepts.append(name)

    language_instruction = ""
    if language != "English":
        language_instruction = f"IMPORTANT: Respond in {language}."

    return TUTOR_SYSTEM_PROMPT.format(
        topic=content[:300] if content else "General topics",
        mastery_info=", ".join(mastery_info) or "No data yet",
        weak_concepts=", ".join(weak_concepts) or "None identified",
        language=language,
        language_instruction=language_instruction,
    )


def chat_with_tutor(
    messages: list[dict],
    system_context: str,
    model_name: str | None = None,
) -> str:
    """
    Send a message to the AI tutor and get a response.

    Args:
        messages: List of message dicts with 'role' and 'content'.
        system_context: The system prompt with student context.
        model_name: Gemini model to use.

    Returns:
        Tutor's response text.
    """
    try:
        client = _get_client()

        # Build contents for the API
        contents = []

        # Add system instruction as the first user message context
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })

        response = client.models.generate_content(
            model=model_name or get_model(),
            contents=contents,
            config={
                "system_instruction": system_context,
                "max_output_tokens": 1000,
                "temperature": 0.7,
            },
        )
        return response.text

    except Exception as e:
        return (
            "I'm having trouble connecting right now. "
            "Please try again in a moment. "
            f"(Error: {type(e).__name__})"
        )


def get_concept_explanation(
    concept_name: str,
    content: str,
    difficulty: str = "beginner",
    language: str = "English",
    model_name: str | None = None,
) -> str:
    """
    Get a detailed explanation of a specific concept.

    Args:
        concept_name: Name of the concept to explain.
        content: Source content for context.
        difficulty: Student's current level.
        language: Language for the explanation.
        model_name: Gemini model to use.

    Returns:
        Detailed explanation text.
    """
    level_instructions = {
        "beginner": "Use very simple language, everyday analogies, and short sentences.",
        "intermediate": "Use moderate complexity with some technical terms explained.",
        "advanced": "Use precise technical language and discuss edge cases.",
    }

    prompt = f"""Explain the concept "{concept_name}" clearly and helpfully.

Context from the study material:
{content[:1000]}

Level: {difficulty}
Style: {level_instructions.get(difficulty, level_instructions['beginner'])}

Provide:
1. A clear explanation (2-3 paragraphs)
2. A real-world analogy
3. 3 key takeaways to remember

{"Write entirely in " + language + "." if language != "English" else ""}"""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model_name or get_model(),
            contents=prompt,
        )
        return response.text
    except Exception:
        return f"Unable to generate explanation for '{concept_name}'. Please check your API key."
