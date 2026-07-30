"""
Manual quiz building - create quizzes without any AI.

Lets the app work fully offline (or when the AI is rate-limited / unavailable):
the user authors their own questions and they flow through the same adaptive
engine, gamification, and results as AI-generated quizzes.
"""

from __future__ import annotations


VALID_TYPES = ("mcq", "true_false", "fill_blank")


def validate_question(q: dict) -> str | None:
    """
    Validate a single manually-entered question.

    Returns an error message string if invalid, or None if the question is OK.
    """
    if not q.get("question", "").strip():
        return "Question text is required."

    q_type = q.get("type")
    if q_type not in VALID_TYPES:
        return f"Unknown question type: {q_type!r}."

    correct = str(q.get("correct_answer", "")).strip()
    if not correct:
        return "A correct answer is required."

    if q_type == "mcq":
        options = [o.strip() for o in q.get("options", []) if o.strip()]
        if len(options) < 2:
            return "Multiple-choice questions need at least 2 options."
        if correct not in options:
            return "The correct answer must be one of the options."

    if q_type == "true_false":
        if correct not in ("True", "False"):
            return "True/False answer must be 'True' or 'False'."

    return None


def build_quiz_from_questions(questions: list[dict], title: str = "My Quiz") -> dict:
    """
    Assemble a quiz dict (concepts + questions) from manual questions.

    Concepts are derived from each question's 'concept' field; questions
    without one are grouped under the quiz title. The returned shape matches
    what the AI path produces, so the rest of the app is unchanged.

    Args:
        questions: List of validated question dicts.
        title: Fallback concept name for questions with no concept.

    Returns:
        {"concepts": [...], "questions": [...]}
    """
    concept_names: list[str] = []
    normalized: list[dict] = []

    for q in questions:
        concept = (q.get("concept") or "").strip() or title
        item = dict(q)
        item["concept"] = concept
        item.setdefault("difficulty", "beginner")
        item.setdefault("explanation", "")
        normalized.append(item)
        if concept not in concept_names:
            concept_names.append(concept)

    concepts = [
        {"name": name, "description": "", "importance": "medium"}
        for name in concept_names
    ]
    return {"concepts": concepts, "questions": normalized}
