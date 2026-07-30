"""
Quiz Engine - Core logic for the Adaptive Quiz Generator.

Modules:
- content_parser: Parse PDFs and text into structured content
- concept_extractor: Identify key concepts from content
- question_generator: Generate quiz questions via Gemini API
- adaptive_logic: Difficulty adaptation state machine
- evaluator: Evaluate answers and generate explanations
- gamification: XP, levels, streaks, and badges
- spaced_repetition: Review scheduling based on mastery
- persistence: Save/load progress as JSON
- study_guide: AI-generated study materials
"""

from quiz_engine.content_parser import parse_pdf, parse_text
from quiz_engine.concept_extractor import extract_concepts
from quiz_engine.question_generator import generate_questions
from quiz_engine.adaptive_logic import AdaptiveEngine
from quiz_engine.evaluator import evaluate_answer, generate_explanation
from quiz_engine.gamification import GamificationEngine
from quiz_engine.spaced_repetition import SpacedRepetitionEngine
from quiz_engine.persistence import export_progress, import_progress

__all__ = [
    "parse_pdf",
    "parse_text",
    "extract_concepts",
    "generate_questions",
    "AdaptiveEngine",
    "evaluate_answer",
    "generate_explanation",
    "GamificationEngine",
    "SpacedRepetitionEngine",
    "export_progress",
    "import_progress",
]
