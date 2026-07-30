"""
Study Guide Generator - Create downloadable study materials.

After a quiz, generates a focused study guide targeting weak areas,
including concept explanations, key takeaways, and practice tips.
"""

from __future__ import annotations

import os
from datetime import datetime
from google import genai

from quiz_engine.llm import get_model


STUDY_GUIDE_PROMPT = """Based on the following quiz results, generate a focused study guide
for the student. Focus on their WEAK areas and provide clear explanations.

Quiz Topic: {topic}
Overall Score: {score_correct}/{score_total} ({percentage:.0f}%)

Concepts that need improvement:
{weak_concepts}

Questions they got wrong:
{wrong_answers}

Generate a study guide in Markdown format with:
1. A brief summary of what they need to focus on
2. For each weak concept:
   - Clear, simple explanation (2-3 paragraphs)
   - A memorable analogy or example
   - 2-3 key points to remember
   - A self-test question they can use later
3. Study tips and next steps

Write in a friendly, encouraging tone. Use Markdown headings and formatting.
"""



def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


def generate_study_guide(
    content: str,
    answers: list[dict],
    concept_states: dict,
    language: str = "English",
    model_name: str | None = None,
) -> str:
    """
    Generate a Markdown study guide focused on weak areas.

    Args:
        content: Original study content.
        answers: List of answer records from the quiz.
        concept_states: Dict of concept states from AdaptiveEngine.
        language: Language for the study guide.
        model_name: Gemini model to use.

    Returns:
        Markdown-formatted study guide string.
    """
    # Identify weak concepts
    weak_concepts = []
    for name, state in concept_states.items():
        if state.mastery_score < 0.8:
            weak_concepts.append(
                f"- {name} (mastery: {state.mastery_score*100:.0f}%, "
                f"got {state.total_correct}/{state.total_attempts} correct)"
            )

    # Identify wrong answers
    wrong_answers = []
    for answer in answers:
        if not answer.get("is_correct", True):
            q = answer.get("question", {})
            wrong_answers.append(
                f"- Q: {q.get('question', 'Unknown')}\n"
                f"  Student answered: {answer.get('student_answer', '?')}\n"
                f"  Correct answer: {q.get('correct_answer', '?')}"
            )

    if not weak_concepts:
        return _generate_perfect_score_guide(concept_states, language)

    # Calculate overall score
    total_correct = sum(s.total_correct for s in concept_states.values())
    total_attempts = sum(s.total_attempts for s in concept_states.values())
    percentage = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    prompt = STUDY_GUIDE_PROMPT.format(
        topic=content[:200] + "..." if len(content) > 200 else content,
        score_correct=total_correct,
        score_total=total_attempts,
        percentage=percentage,
        weak_concepts="\n".join(weak_concepts) or "None",
        wrong_answers="\n".join(wrong_answers[:10]) or "None",
    )

    if language != "English":
        prompt += f"\n\nIMPORTANT: Write the entire study guide in {language}."

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model_name or get_model(),
            contents=prompt,
        )
        return response.text
    except Exception:
        return _generate_fallback_guide(weak_concepts, wrong_answers, percentage)



def _generate_perfect_score_guide(concept_states: dict, language: str) -> str:
    """Generate a congratulatory guide when all concepts are mastered."""
    concepts_list = "\n".join(
        f"- **{name}** ({state.mastery_score*100:.0f}% mastery)"
        for name, state in concept_states.items()
    )
    return f"""# Congratulations! Perfect Performance!

You've demonstrated strong understanding across all concepts:

{concepts_list}

## Next Steps

- Try increasing the difficulty level on your next attempt
- Explore related topics to deepen your knowledge
- Come back in a few days to test your long-term retention

Keep up the excellent work!
"""


def _generate_fallback_guide(
    weak_concepts: list[str],
    wrong_answers: list[str],
    percentage: float,
) -> str:
    """Generate a basic study guide when AI is unavailable."""
    guide = f"""# Study Guide

## Your Score: {percentage:.0f}%

## Areas to Focus On

{chr(10).join(weak_concepts)}

## Questions to Review

{chr(10).join(wrong_answers[:5])}

## Study Tips

1. Re-read the source material focusing on the weak concepts above
2. Try to explain each concept in your own words
3. Come back and take the quiz again after reviewing
4. Focus on understanding *why* the correct answers are correct

---
*Generated on {datetime.now().strftime("%B %d, %Y")}*
"""
    return guide
