"""
Adaptive Logic - Difficulty adaptation state machine.

Tracks user performance per concept and adjusts difficulty dynamically.
Implements a simple but effective adaptation algorithm:
- 2 correct in a row -> level up
- 1 wrong -> explain + easier follow-up
- 3 wrong on same concept -> flag for review, move on
"""

from __future__ import annotations

from dataclasses import dataclass, field


DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]


@dataclass
class ConceptState:
    """Tracks performance state for a single concept."""
    name: str
    level: int = 0                # Index into DIFFICULTY_LEVELS
    correct_streak: int = 0       # Consecutive correct answers
    total_correct: int = 0
    total_attempts: int = 0
    needs_review: bool = False    # Flagged for extra practice

    @property
    def difficulty(self) -> str:
        """Get current difficulty level as string."""
        return DIFFICULTY_LEVELS[self.level]

    @property
    def mastery_score(self) -> float:
        """Calculate mastery percentage (0.0 to 1.0)."""
        if self.total_attempts == 0:
            return 0.0
        return self.total_correct / self.total_attempts


@dataclass
class AdaptiveEngine:
    """
    Manages adaptive difficulty across all concepts.

    Tracks performance per concept, decides when to level up/down,
    and determines which concepts need more practice.
    """
    concept_states: dict = field(default_factory=dict)  # name -> ConceptState
    history: list = field(default_factory=list)          # Full answer history

    def register_concepts(self, concepts: list[dict]):
        """Initialize tracking for a list of concepts."""
        for concept in concepts:
            name = concept["name"]
            if name not in self.concept_states:
                self.concept_states[name] = ConceptState(name=name)

    def record_answer(self, concept_name: str, is_correct: bool) -> dict:
        """
        Record an answer and return adaptation decision.

        Args:
            concept_name: The concept being tested.
            is_correct: Whether the user answered correctly.

        Returns:
            Dictionary with adaptation action and details.
        """
        state = self.concept_states.get(concept_name)
        if not state:
            state = ConceptState(name=concept_name)
            self.concept_states[concept_name] = state

        state.total_attempts += 1

        # Record in history
        self.history.append({
            "concept": concept_name,
            "correct": is_correct,
            "difficulty": state.difficulty,
        })

        if is_correct:
            state.total_correct += 1
            state.correct_streak += 1

            # Level up after 2 correct in a row
            if state.correct_streak >= 2 and state.level < len(DIFFICULTY_LEVELS) - 1:
                state.level += 1
                state.correct_streak = 0
                return {
                    "action": "level_up",
                    "new_difficulty": state.difficulty,
                    "message": f"Great job! Increasing difficulty to {state.difficulty}.",
                }

            return {
                "action": "continue",
                "message": "Correct! Keep going.",
            }
        else:
            state.correct_streak = 0

            # Count recent failures on this concept
            recent_failures = sum(
                1 for h in self.history[-5:]
                if h["concept"] == concept_name and not h["correct"]
            )

            if recent_failures >= 3:
                state.needs_review = True
                return {
                    "action": "flag_review",
                    "message": f"Let's move on. '{concept_name}' is flagged for extra review later.",
                }

            # Level down if not already at beginner
            if state.level > 0:
                state.level -= 1

            return {
                "action": "explain_and_retry",
                "new_difficulty": state.difficulty,
                "message": "Let me explain this concept and try an easier question.",
            }

    def get_current_difficulty(self, concept_name: str) -> str:
        """Get the current difficulty level for a concept."""
        state = self.concept_states.get(concept_name)
        if not state:
            return DIFFICULTY_LEVELS[0]
        return state.difficulty

    def get_weakest_concepts(self, top_n: int = 3) -> list[ConceptState]:
        """Get the concepts with lowest mastery scores."""
        states = list(self.concept_states.values())
        states.sort(key=lambda s: s.mastery_score)
        return states[:top_n]

    def get_concepts_for_review(self) -> list[ConceptState]:
        """Get all concepts flagged for review."""
        return [s for s in self.concept_states.values() if s.needs_review]

    def get_overall_score(self) -> dict:
        """Calculate overall quiz performance summary."""
        total_correct = sum(s.total_correct for s in self.concept_states.values())
        total_attempts = sum(s.total_attempts for s in self.concept_states.values())

        return {
            "total_correct": total_correct,
            "total_attempts": total_attempts,
            "percentage": (total_correct / total_attempts * 100) if total_attempts > 0 else 0,
            "concepts_mastered": sum(
                1 for s in self.concept_states.values() if s.mastery_score >= 0.8
            ),
            "concepts_needing_review": len(self.get_concepts_for_review()),
        }
