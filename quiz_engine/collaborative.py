"""
Collaborative Mode - Share quizzes and compare scores.

Generates shareable quiz codes (JSON-encoded) that others can
import to take the same quiz and compare results.
"""

from __future__ import annotations

import json
import hashlib
import base64
from datetime import datetime


def generate_quiz_code(
    content_source: str,
    questions: list[dict],
    concepts: list[dict],
    creator_name: str = "Anonymous",
    language: str = "English",
) -> str:
    """
    Generate a shareable quiz code containing all quiz data.

    Args:
        content_source: Brief description of the source material.
        questions: List of generated questions.
        concepts: List of extracted concepts.
        creator_name: Name of the quiz creator.
        language: Language the quiz is in.

    Returns:
        Base64-encoded JSON string that can be shared.
    """
    quiz_data = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "creator": creator_name,
        "language": language,
        "source_description": content_source[:200],
        "concepts": concepts,
        "questions": questions,
        "leaderboard": [],
    }

    json_str = json.dumps(quiz_data, separators=(",", ":"))
    encoded = base64.b64encode(json_str.encode()).decode()

    # Create a short ID from hash
    short_id = hashlib.md5(json_str.encode()).hexdigest()[:8].upper()

    return f"QUIZ-{short_id}-{encoded}"



def import_quiz_code(code: str) -> dict | None:
    """
    Import a quiz from a shared code.

    Args:
        code: The shared quiz code string.

    Returns:
        Quiz data dictionary, or None if invalid.
    """
    try:
        # Strip prefix
        if code.startswith("QUIZ-"):
            parts = code.split("-", 2)
            if len(parts) == 3:
                encoded = parts[2]
            else:
                encoded = code
        else:
            encoded = code

        json_str = base64.b64decode(encoded).decode()
        quiz_data = json.loads(json_str)

        # Validate required fields
        required = ["questions", "concepts"]
        for field in required:
            if field not in quiz_data:
                return None

        return quiz_data

    except Exception:
        return None


def add_score_to_leaderboard(
    quiz_data: dict,
    player_name: str,
    score_correct: int,
    score_total: int,
    time_seconds: int = 0,
) -> dict:
    """
    Add a player's score to the quiz leaderboard.

    Args:
        quiz_data: The quiz data dictionary.
        player_name: Player's display name.
        score_correct: Number of correct answers.
        score_total: Total number of questions.
        time_seconds: Time taken in seconds.

    Returns:
        Updated quiz data with the new score.
    """
    percentage = (score_correct / score_total * 100) if score_total > 0 else 0

    entry = {
        "player": player_name,
        "score_correct": score_correct,
        "score_total": score_total,
        "percentage": percentage,
        "time_seconds": time_seconds,
        "timestamp": datetime.now().isoformat(),
    }

    if "leaderboard" not in quiz_data:
        quiz_data["leaderboard"] = []

    quiz_data["leaderboard"].append(entry)

    # Sort by percentage (desc), then time (asc)
    quiz_data["leaderboard"].sort(
        key=lambda x: (-x["percentage"], x.get("time_seconds", 9999))
    )

    return quiz_data


def get_leaderboard_display(quiz_data: dict) -> list[dict]:
    """
    Get formatted leaderboard for display.

    Returns:
        List of leaderboard entries with rank.
    """
    leaderboard = quiz_data.get("leaderboard", [])
    display = []

    for i, entry in enumerate(leaderboard[:10]):
        medals = {0: "gold", 1: "silver", 2: "bronze"}
        display.append({
            "rank": i + 1,
            "medal": medals.get(i, ""),
            "player": entry["player"],
            "score": f"{entry['score_correct']}/{entry['score_total']}",
            "percentage": f"{entry['percentage']:.0f}%",
            "time": f"{entry.get('time_seconds', 0)}s" if entry.get("time_seconds") else "-",
        })

    return display
