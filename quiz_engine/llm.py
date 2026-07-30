"""
Central LLM configuration and client helpers.

One place to control the Gemini model and client creation, so a model
deprecation only requires changing a single default (or setting an env var).

The model can be overridden without code changes by setting GEMINI_MODEL
in the environment or in Streamlit secrets (bridged to env at startup).
"""

from __future__ import annotations

import os
import time
from google import genai


# Default model. Gemini 2.0 Flash was shut down on 2026-06-01, so we target a
# current, generally-available Flash model. Override with the GEMINI_MODEL
# environment variable / secret if Google changes availability again.
DEFAULT_MODEL = "gemini-2.5-flash"

# If the primary model is overloaded (503) or unavailable, try these in order.
# Kept short and ordered by stability/availability on the free tier.
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
]

# Retry settings for transient server errors (503/overloaded, 429/rate limit).
_MAX_ATTEMPTS_PER_MODEL = 3
_BACKOFF_BASE_SECONDS = 1.5


class GenerationError(Exception):
    """Raised when an LLM generation call fails, with a user-friendly message."""


def get_model() -> str:
    """Return the configured Gemini model name."""
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def _is_overload(exc: Exception) -> bool:
    """True for a temporary server overload (503) worth retrying on the same model."""
    low = str(exc).lower()
    return any(s in low for s in ("503", "unavailable", "overloaded"))


def _is_rate_limit(exc: Exception) -> bool:
    """True for a quota / rate-limit error (429). Retrying the same model won't help."""
    low = str(exc).lower()
    return any(s in low for s in ("429", "resource_exhausted", "quota", "rate limit", "rate-limit"))


def _is_transient(exc: Exception) -> bool:
    """True for any error where trying another model may help."""
    return _is_overload(exc) or _is_rate_limit(exc)


def _is_model_unavailable(exc: Exception) -> bool:
    """True when the model itself is missing/unsupported (try a different model)."""
    low = str(exc).lower()
    return any(s in low for s in ("404", "not found", "not supported", "does not exist"))


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
    if "503" in low or "unavailable" in low or "overloaded" in low:
        return (
            "Gemini is temporarily overloaded (503). We retried and tried backup "
            "models but they're all busy right now - please try again in a moment."
        )
    if "429" in low or "quota" in low or "rate" in low or "resource_exhausted" in low:
        return (
            "Gemini rate limit / quota reached. Wait a moment and try again, or "
            "check your usage limits in Google AI Studio."
        )
    return f"The AI request failed: {text[:200]}"


def _candidate_models(model: str | None) -> list[str]:
    """Build the ordered list of models to attempt (primary first, then fallbacks)."""
    primary = model or get_model()
    candidates = [primary]
    for m in FALLBACK_MODELS:
        if m not in candidates:
            candidates.append(m)
    return candidates


def generate_text(prompt: str, model: str | None = None) -> str:
    """
    Call Gemini to generate text, with retry-on-overload and model fallback.

    - Retries transient errors (503 overloaded, 429 rate limit) with backoff.
    - Falls back to alternate models if one is unavailable or stays overloaded.
    - Raises GenerationError with a friendly message if everything fails, so
      callers can surface it in the UI instead of crashing.
    """
    client = get_client()
    last_exc: Exception | None = None

    for model_name in _candidate_models(model):
        for attempt in range(_MAX_ATTEMPTS_PER_MODEL):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as exc:  # noqa: BLE001 - wrap all API errors
                last_exc = exc

                # 503 overload: brief backoff, then retry the SAME model
                if _is_overload(exc) and attempt < _MAX_ATTEMPTS_PER_MODEL - 1:
                    time.sleep(_BACKOFF_BASE_SECONDS * (2 ** attempt))
                    continue

                # For rate-limit (429), model-unavailable, or exhausted overload
                # retries, move on to the next candidate model (fresh rate bucket).
                # Retrying the same model on a 429 only burns more quota.
                if _is_rate_limit(exc) or _is_model_unavailable(exc) or _is_overload(exc):
                    break

                # Hard errors (bad key, malformed request): fallback won't help.
                raise GenerationError(_friendly_message(exc)) from exc

    raise GenerationError(_friendly_message(last_exc or Exception("unknown error")))
