"""
Central LLM configuration and client helpers.

One place to control the Gemini model and client creation, so a model
deprecation only requires changing a single default (or setting an env var).

The model can be overridden without code changes by setting GEMINI_MODEL
in the environment or in Streamlit secrets (bridged to env at startup).
"""

from __future__ import annotations

import os
from google import genai


# Default model. Gemini 2.0 Flash was shut down on 2026-06-01, so we target a
# current, generally-available Flash model. Override with the GEMINI_MODEL
# environment variable / secret if Google changes availability again.
DEFAULT_MODEL = "gemini-2.5-flash"


class GenerationError(Exception):
    """Raised when an LLM generation call fails, with a user-friendly message."""


def get_model() -> str:
    """Return the configured Gemini model name."""
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def get_client() -> genai.Client:
    """Create a Gemini client using the configured API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


def _friendly_message(exc: Exception) -> str:
    """Turn a raw google-genai error into a short, actionable message."""
    text = str(exc)
    low = text.lower()
    model = get_model()

    if "api key" in low or "api_key" in low or "permission" in low or "403" in low:
        return (
            "Your Gemini API key was rejected. Double-check GEMINI_API_KEY in "
            "the app Secrets, and that the Generative Language API is enabled."
        )
    if "not found" in low or "404" in low or "not supported" in low:
        return (
            f"The model '{model}' is unavailable for your key. Set a GEMINI_MODEL "
            "secret to a current model (e.g. gemini-2.5-flash or gemini-3.5-flash)."
        )
    if "429" in low or "quota" in low or "rate" in low or "resource_exhausted" in low:
        return (
            "Gemini rate limit / quota reached. Wait a moment and try again, or "
            "check your usage limits in Google AI Studio."
        )
    return f"The AI request failed: {text[:200]}"


def generate_text(prompt: str, model: str | None = None) -> str:
    """
    Call Gemini to generate text from a prompt.

    Raises GenerationError with a friendly message on any failure so callers
    can surface it in the UI instead of crashing.
    """
    try:
        client = get_client()
        response = client.models.generate_content(
            model=model or get_model(),
            contents=prompt,
        )
        return response.text
    except Exception as exc:  # noqa: BLE001 - we deliberately wrap all API errors
        raise GenerationError(_friendly_message(exc)) from exc
