"""
Question Generator - Generate quiz questions via Gemini API.

Creates varied question types (MCQ, True/False, Fill-in-the-blank)
at specified difficulty levels for given concepts.
"""

from __future__ import annotations

import json

from quiz_engine.llm import generate_text, get_model


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
