"""
Persistence - Save and load quiz progress as JSON.

Handles export/import of:
- Quiz history and scores
- Gamification state (XP, badges, streaks)
- Spaced repetition schedule
"""

from __future__ import annotations

import json
from datetime import datetime

from quiz_engine.gamification import GamificationEngine
from quiz_engine.spaced_repetition import SpacedRepetitionEngine


def export_progress(
    gamification: GamificationEngine,
    spaced_rep: SpacedRepetitionEngine,
    quiz_history: list[dict] | None = None,
) -> str:
    """
    Export all progress data as a JSON string.

    Args:
        gamification: GamificationEngine instance.
        spaced_rep: SpacedRepetitionEngine instance.
        quiz_history: Optional list of past quiz summaries.

    Returns:
        JSON string of all progress data.
    """
    data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "gamification": gamification.to_dict(),
        "spaced_repetition": spaced_rep.to_dict(),
        "quiz_history": quiz_history or [],
    }
    return json.dumps(data, indent=2)



def import_progress(json_string: str) -> dict:
    """
    Import progress data from a JSON string.

    Args:
        json_string: JSON string previously exported.

    Returns:
        Dictionary with 'gamification', 'spaced_repetition', and 'quiz_history'.
    """
    data = json.loads(json_string)

    gamification = GamificationEngine.from_dict(
        data.get("gamification", {})
    )
    spaced_rep = SpacedRepetitionEngine.from_dict(
        data.get("spaced_repetition", {})
    )
    quiz_history = data.get("quiz_history", [])

    return {
        "gamification": gamification,
        "spaced_repetition": spaced_rep,
        "quiz_history": quiz_history,
    }


def create_quiz_summary(
    content_source: str,
    concepts: list[dict],
    answers: list[dict],
    overall_score: dict,
    language: str = "English",
) -> dict:
    """
    Create a summary of a completed quiz for history tracking.

    Args:
        content_source: Description of what was studied.
        concepts: List of concept dicts.
        answers: List of answer records.
        overall_score: Overall score dict from AdaptiveEngine.
        language: Language the quiz was taken in.

    Returns:
        Quiz summary dictionary.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "content_source": content_source[:200],
        "num_concepts": len(concepts),
        "num_questions": overall_score.get("total_attempts", 0),
        "score_correct": overall_score.get("total_correct", 0),
        "score_percentage": overall_score.get("percentage", 0),
        "language": language,
        "concepts_mastered": overall_score.get("concepts_mastered", 0),
        "concepts_needing_review": overall_score.get("concepts_needing_review", 0),
    }
