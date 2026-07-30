"""
Concept Extractor - Identify key concepts from content using Gemini.

Uses the LLM to analyze text and extract discrete, testable concepts
that can be used to generate targeted quiz questions.
"""

from __future__ import annotations

import json
import os
from google import genai


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


def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


def extract_concepts(
    content: str,
    model_name: str = "gemini-2.0-flash",
    language: str = "English",
) -> list[dict]:
    """
    Extract key concepts from content using Gemini API.

    Args:
        content: Text content to analyze.
        model_name: Gemini model to use.
        language: Language for concept names and descriptions.

    Returns:
        List of concept dictionaries with name, description, and importance.
    """
    client = _get_client()
    prompt = EXTRACTION_PROMPT.format(content=content[:4000])  # Limit input size

    if language != "English":
        prompt += f"\n\nIMPORTANT: Write the concept names and descriptions in {language}."

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    response_text = response.text.strip()

    # Clean up response - remove markdown code blocks if present
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    concepts = json.loads(response_text)
    return concepts
