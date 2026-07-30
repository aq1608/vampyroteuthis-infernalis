"""
Evaluator - Check answers and generate explanations via Gemini.

Handles:
- Exact matching for MCQ and True/False
- Fuzzy/semantic matching for short answer questions
- Generating helpful explanations for wrong answers
- Creating simpler follow-up questions
"""

from __future__ import annotations

import json
import os
from google import genai

from quiz_engine.llm import get_model


EXPLANATION_PROMPT = """The student answered a quiz question incorrectly.

Question: {question}
Student's Answer: {student_answer}
Correct Answer: {correct_answer}
Concept Being Tested: {concept}

Please provide:
1. A clear, friendly explanation (2-3 sentences) of why the correct answer is right
2. If helpful, use an analogy or simple example
3. A simpler follow-up question to check their understanding

Return as JSON:
{{
    "explanation": "Your explanation here...",
    "tip": "A short memory aid or key takeaway",
    "follow_up_question": {{
        "question": "A simpler question on the same concept",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "{concept}",
        "difficulty": "beginner",
        "explanation": "Why this answer is correct"
    }}
}}

Return ONLY the JSON, no other text."""


SEMANTIC_EVAL_PROMPT = """Evaluate if the student's answer is correct for this fill-in-the-blank question.

Question: {question}
Expected Answer: {correct_answer}
Student's Answer: {student_answer}

The student's answer doesn't need to be word-for-word identical, but must demonstrate
the same core understanding. Be reasonably lenient with phrasing but strict on accuracy.

Return as JSON:
{{
    "is_correct": true/false,
    "reason": "Brief explanation of your evaluation"
}}

Return ONLY the JSON, no other text."""


def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


def evaluate_answer(question: dict, student_answer: str) -> dict:
    """
    Evaluate a student's answer against the correct answer.

    Args:
        question: Question dictionary with correct_answer, type, etc.
        student_answer: The student's submitted answer.

    Returns:
        Dictionary with is_correct boolean and evaluation details.
    """
    correct = question["correct_answer"]
    q_type = question.get("type", "mcq")

    # For MCQ and True/False: exact match (case-insensitive)
    if q_type in ("mcq", "true_false"):
        is_correct = student_answer.strip().lower() == correct.strip().lower()
        return {
            "is_correct": is_correct,
            "correct_answer": correct,
            "student_answer": student_answer,
        }

    # For fill-in-the-blank: try semantic evaluation, fallback to fuzzy match
    if q_type == "fill_blank":
        return _semantic_evaluate(question, student_answer)

    # Fallback: exact match
    is_correct = student_answer.strip().lower() == correct.strip().lower()
    return {
        "is_correct": is_correct,
        "correct_answer": correct,
        "student_answer": student_answer,
    }


def _fuzzy_match(student_answer: str, correct_answer: str) -> bool:
    """
    Simple fuzzy matching fallback when API is unavailable.
    Checks if the core of the answer matches.
    """
    student = student_answer.strip().lower()
    correct = correct_answer.strip().lower()

    # Exact match
    if student == correct:
        return True

    # Check if one contains the other
    if student in correct or correct in student:
        return True

    # Check word overlap (at least 60% of correct answer words present)
    correct_words = set(correct.split())
    student_words = set(student.split())
    if len(correct_words) > 0:
        overlap = len(correct_words & student_words) / len(correct_words)
        if overlap >= 0.6:
            return True

    return False


def _semantic_evaluate(
    question: dict, student_answer: str, model_name: str | None = None
) -> dict:
    """
    Use Gemini to semantically evaluate a short answer.
    Falls back to fuzzy matching if API is unavailable.
    """
    try:
        client = _get_client()

        prompt = SEMANTIC_EVAL_PROMPT.format(
            question=question["question"],
            correct_answer=question["correct_answer"],
            student_answer=student_answer,
        )

        response = client.models.generate_content(
            model=model_name or get_model(),
            contents=prompt,
        )
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        result = json.loads(response_text)
        result["correct_answer"] = question["correct_answer"]
        result["student_answer"] = student_answer
        return result

    except Exception:
        # Fallback to fuzzy matching if API fails
        is_correct = _fuzzy_match(student_answer, question["correct_answer"])
        return {
            "is_correct": is_correct,
            "correct_answer": question["correct_answer"],
            "student_answer": student_answer,
            "reason": "Evaluated using text similarity (API unavailable)",
        }


def generate_explanation(
    question: dict, student_answer: str, model_name: str | None = None
) -> dict:
    """
    Generate a helpful explanation for a wrong answer.

    Args:
        question: The question dictionary.
        student_answer: The student's incorrect answer.
        model_name: Gemini model to use.

    Returns:
        Dictionary with explanation, tip, and follow-up question.
    """
    try:
        client = _get_client()

        prompt = EXPLANATION_PROMPT.format(
            question=question["question"],
            student_answer=student_answer,
            correct_answer=question["correct_answer"],
            concept=question.get("concept", "General"),
        )

        response = client.models.generate_content(
            model=model_name or get_model(),
            contents=prompt,
        )
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        result = json.loads(response_text)
        return result

    except Exception:
        # Fallback explanation when API is unavailable
        return {
            "explanation": f"The correct answer is '{question['correct_answer']}'. Review this concept and try again.",
            "tip": "Focus on understanding the key idea behind this concept.",
            "follow_up_question": None,
        }
