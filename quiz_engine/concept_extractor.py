"""
Concept Extractor - Identify key concepts from content using Gemini.

Uses the LLM to analyze text and extract discrete, testable concepts
that can be used to generate targeted quiz questions.
"""

from __future__ import annotations

import json

from quiz_engine.llm import generate_text, get_model


EXTRACTION_PROMPT = """Analyze the following text and extract the key concepts that a student should understand.

For each concept, provide:
- name: A short label (2-5 words)
- description: A one-sentence summary of what the concept means
- importance: "high", "medium", or "low" based on how central it is to the text

Return your response as a JSON array. Example:
[
    {{"name": "Photosynthesis", "description": "The process by which plants convert sunlight into energy.", "importance": "high"}},
    {{"name": "Chlorophyll", "description": "The green pigment in plants that absorbs light energy.", "importance": "medium"}}
]

Extract between 3 and 8 concepts. Focus on the most important, testable ideas.

Text:
{content}

Return ONLY the JSON array, no other text."""


def extract_concepts(
    content: str,
    model_name: str | None = None,
    language: str = "English",
) -> list[dict]:
    """
    Extract key concepts from content using Gemini API.

    Args:
        content: Text content to analyze.
        model_name: Gemini model to use (defaults to the configured model).
        language: Language for concept names and descriptions.

    Returns:
        List of concept dictionaries with name, description, and importance.
    """
    prompt = EXTRACTION_PROMPT.format(content=content[:4000])  # Limit input size

    if language != "English":
        prompt += f"\n\nIMPORTANT: Write the concept names and descriptions in {language}."

    response_text = generate_text(prompt, model=model_name or get_model()).strip()

    # Clean up response - remove markdown code blocks if present
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    concepts = json.loads(response_text)
    return concepts
