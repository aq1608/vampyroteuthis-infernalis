"""
Question Generator - Generate quiz questions via Gemini API.

Creates varied question types (MCQ, True/False, Fill-in-the-blank)
at specified difficulty levels for given concepts.
"""

from __future__ import annotations

import json

from quiz_engine.llm import generate_text, get_model
from quiz_engine.evaluator import closest_option


def _repair_mcq_answers(questions: list[dict]) -> list[dict]:
    """
    Align each MCQ's correct_answer with an actual option.

    Models occasionally return a correct_answer that doesn't verbatim match any
    option (label prefixes, casing, slight rewording), which would make a right
    pick score wrong and show a "correct answer" that isn't one of the choices.
    Repairing here keeps grading and display consistent.
    """
    for q in questions:
        if q.get("type") != "mcq":
            continue
        options = q.get("options", [])
        correct = q.get("correct_answer", "")
        if options and correct not in options:
            match = closest_option(correct, options)
            if match is not None:
                q["correct_answer"] = match
    return questions


GENERATION_PROMPT = """Generate {num_questions} quiz question(s) about the following concept.

Concept: {concept_name}
Concept Description: {concept_description}
Source Material: {content_excerpt}
Difficulty Level: {difficulty}

Rules:
- Difficulty "beginner": Basic recall and simple understanding
- Difficulty "intermediate": Application and analysis
- Difficulty "advanced": Synthesis, evaluation, and edge cases
- Mix question types: "mcq" (multiple choice), "true_false", "fill_blank" (short answer)
- For MCQ: provide exactly 4 options, one correct
- Questions should test understanding, not just memorization

Return as a JSON array. Example:
[
    {{
        "question": "What is the primary function of mitochondria?",
        "type": "mcq",
        "options": ["Energy production", "Protein synthesis", "Cell division", "Waste removal"],
        "correct_answer": "Energy production",
        "concept": "Mitochondria",
        "difficulty": "beginner",
        "explanation": "Mitochondria are known as the powerhouse of the cell because they produce ATP through cellular respiration."
    }},
    {{
        "question": "Mitochondria have their own DNA separate from the cell nucleus.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Mitochondria",
        "difficulty": "intermediate",
        "explanation": "Mitochondria contain their own circular DNA, which supports the endosymbiotic theory of their origin."
    }}
]

Return ONLY the JSON array, no other text."""


FULL_QUIZ_PROMPT = """You are building a study quiz from the material below.

Do BOTH of these in a single response:
1. Identify {num_concepts} key concepts a student should understand.
2. For EACH concept, write {questions_per_concept} quiz questions at "{difficulty}" difficulty.

Rules:
- Difficulty "beginner": basic recall; "intermediate": application/analysis; "advanced": synthesis/edge cases
- Mix question types: "mcq" (exactly 4 options, one correct), "true_false", "fill_blank" (short answer)
- Questions must test understanding, not rote memorization
- Every question's "concept" field must match one of the concept names exactly

Source Material:
{content}

Return ONLY this JSON object (no other text):
{{
  "concepts": [
    {{"name": "Concept Name", "description": "One-sentence summary.", "importance": "high"}}
  ],
  "questions": [
    {{
      "question": "...",
      "type": "mcq",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "concept": "Concept Name",
      "difficulty": "{difficulty}",
      "explanation": "Why the answer is correct."
    }}
  ]
}}"""


def generate_full_quiz(
    content: str,
    difficulty: str = "beginner",
    num_concepts: int = 4,
    questions_per_concept: int = 2,
    model_name: str | None = None,
    language: str = "English",
) -> dict:
    """
    Generate concepts AND all questions in a SINGLE API call.

    This is the quota-friendly path: one request produces the whole quiz,
    instead of one call per concept. Returns a dict with "concepts" and
    "questions" lists. Raises GenerationError (from generate_text) on failure.

    Args:
        content: Source study material.
        difficulty: Starting difficulty level.
        num_concepts: How many concepts to extract.
        questions_per_concept: Questions to write per concept.
        model_name: Gemini model to use (defaults to configured model).
        language: Output language.

    Returns:
        {"concepts": [...], "questions": [...]}
    """
    prompt = FULL_QUIZ_PROMPT.format(
        num_concepts=num_concepts,
        questions_per_concept=questions_per_concept,
        difficulty=difficulty,
        content=content[:4000],
    )
    if language != "English":
        prompt += f"\n\nIMPORTANT: Write all concept names, descriptions, questions, options, answers, and explanations in {language}."

    response_text = generate_text(prompt, model=model_name or get_model()).strip()

    # Strip markdown code fences if present
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    data = json.loads(response_text)
    concepts = data.get("concepts", [])
    questions = data.get("questions", [])

    # Safety: ensure every question references a known concept
    valid_names = {c["name"] for c in concepts}
    for q in questions:
        if q.get("concept") not in valid_names and concepts:
            q["concept"] = concepts[0]["name"]

    _repair_mcq_answers(questions)

    return {"concepts": concepts, "questions": questions}


def generate_questions(
    concept: dict,
    content: str,
    difficulty: str = "beginner",
    num_questions: int = 2,
    model_name: str | None = None,
    language: str = "English",
) -> list[dict]:
    """
    Generate quiz questions for a specific concept at a given difficulty.

    Args:
        concept: Dictionary with concept name and description.
        content: Source content for context.
        difficulty: One of "beginner", "intermediate", "advanced".
        num_questions: Number of questions to generate.
        model_name: Gemini model to use.
        language: Language for questions and answers.

    Returns:
        List of question dictionaries.
    """
    prompt = GENERATION_PROMPT.format(
        num_questions=num_questions,
        concept_name=concept["name"],
        concept_description=concept["description"],
        content_excerpt=content[:2000],
        difficulty=difficulty,
    )

    if language != "English":
        prompt += f"\n\nIMPORTANT: Write all questions, options, answers, and explanations in {language}."

    response_text = generate_text(prompt, model=model_name or get_model()).strip()

    # Clean up response - remove markdown code blocks if present
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    questions = json.loads(response_text)
    _repair_mcq_answers(questions)
    return questions


def generate_quiz_batch(
    concepts: list[dict],
    content: str,
    difficulty: str = "beginner",
    questions_per_concept: int = 2,
    language: str = "English",
) -> list[dict]:
    """
    Generate a full batch of questions across multiple concepts.

    Args:
        concepts: List of concept dictionaries.
        content: Source content for context.
        difficulty: Starting difficulty level.
        questions_per_concept: Number of questions per concept.
        language: Language for questions.

    Returns:
        Flat list of all generated questions.
    """
    all_questions = []
    for concept in concepts:
        questions = generate_questions(
            concept=concept,
            content=content,
            difficulty=difficulty,
            num_questions=questions_per_concept,
            language=language,
        )
        all_questions.extend(questions)
    return all_questions
