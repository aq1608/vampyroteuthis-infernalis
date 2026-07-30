"""
Live shared leaderboard backed by Supabase (Postgres).

Optional: if SUPABASE_URL / SUPABASE_KEY are not configured (or the supabase
package is not installed), every function degrades gracefully - submits become
no-ops and fetches return an empty list - so the app still works fully offline
using the code-passing leaderboard in `collaborative.py`.

Scores are keyed by a stable `quiz_id` (a content hash of the questions, from
collaborative.compute_quiz_id), so everyone playing the same shared quiz writes
to and reads from the same leaderboard.

Setup (run once in the Supabase SQL editor) lives in supabase_schema.sql.
"""

from __future__ import annotations

import os

TABLE = "quiz_scores"

# Cached client so we don't rebuild it on every Streamlit rerun.
_client = None


def _get_credentials() -> tuple[str | None, str | None]:
    """Return (url, anon_key) from the environment (bridged from st.secrets)."""
    return os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")


def is_configured() -> bool:
    """True only if both credentials are present AND the supabase package exists."""
    url, key = _get_credentials()
    if not (url and key):
        return False
    try:
        import supabase  # noqa: F401
    except Exception:
        return False
    return True


def _get_client():
    """Create (and cache) the Supabase client. Assumes is_configured() is True."""
    global _client
    if _client is not None:
        return _client
    from supabase import create_client
    url, key = _get_credentials()
    _client = create_client(url, key)
    return _client


def submit_score(
    quiz_id: str,
    player: str,
    score_correct: int,
    score_total: int,
    time_seconds: int = 0,
) -> bool:
    """
    Insert one score row for a quiz. Returns True on success, False otherwise.

    Never raises - a leaderboard write must not break the results page.
    """
    if not is_configured():
        return False
    try:
        percentage = (score_correct / score_total * 100) if score_total else 0
        _get_client().table(TABLE).insert({
            "quiz_id": quiz_id,
            "player": player or "Anonymous",
            "score_correct": score_correct,
            "score_total": score_total,
            "percentage": percentage,
            "time_seconds": time_seconds,
        }).execute()
        return True
    except Exception:
        return False


def fetch_leaderboard(quiz_id: str, limit: int = 10) -> list[dict]:
    """
    Return the top scores for a quiz (best percentage first, then fastest time).

    Returns an empty list if not configured or on any error.
    """
    if not is_configured() or not quiz_id:
        return []
    try:
        response = (
            _get_client()
            .table(TABLE)
            .select("player, score_correct, score_total, percentage, time_seconds")
            .eq("quiz_id", quiz_id)
            .order("percentage", desc=True)
            .order("time_seconds", desc=False)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception:
        return []
