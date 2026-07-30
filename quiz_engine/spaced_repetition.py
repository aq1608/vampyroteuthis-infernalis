"""
Spaced Repetition - Track weak concepts and schedule reviews.

Implements a simplified spaced repetition system based on
concept mastery scores and time since last review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


# Review intervals based on mastery level
REVIEW_INTERVALS = {
    "critical": timedelta(minutes=5),    # < 30% mastery
    "weak": timedelta(hours=1),          # 30-50% mastery
    "moderate": timedelta(hours=6),      # 50-70% mastery
    "strong": timedelta(days=1),         # 70-90% mastery
    "mastered": timedelta(days=3),       # > 90% mastery
}



def _get_mastery_level(mastery: float) -> str:
    """Classify mastery score into a level."""
    if mastery < 0.3:
        return "critical"
    elif mastery < 0.5:
        return "weak"
    elif mastery < 0.7:
        return "moderate"
    elif mastery < 0.9:
        return "strong"
    else:
        return "mastered"


@dataclass
class ReviewItem:
    """A concept scheduled for review."""
    concept_name: str
    concept_description: str
    mastery_score: float
    last_reviewed: str  # ISO format datetime string
    next_review: str    # ISO format datetime string
    review_count: int = 0

    @property
    def mastery_level(self) -> str:
        return _get_mastery_level(self.mastery_score)

    @property
    def is_due(self) -> bool:
        """Check if this item is due for review."""
        now = datetime.now()
        next_dt = datetime.fromisoformat(self.next_review)
        return now >= next_dt

    def to_dict(self) -> dict:
        return {
            "concept_name": self.concept_name,
            "concept_description": self.concept_description,
            "mastery_score": self.mastery_score,
            "last_reviewed": self.last_reviewed,
            "next_review": self.next_review,
            "review_count": self.review_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewItem":
        return cls(**data)



@dataclass
class SpacedRepetitionEngine:
    """Manages spaced repetition review schedule."""
    review_items: dict = field(default_factory=dict)  # concept_name -> ReviewItem

    def add_concepts_from_quiz(self, concept_states: dict):
        """
        After a quiz, add/update concepts in the review schedule.

        Args:
            concept_states: Dict of concept_name -> ConceptState from AdaptiveEngine
        """
        now = datetime.now()

        for name, state in concept_states.items():
            mastery = state.mastery_score
            level = _get_mastery_level(mastery)
            interval = REVIEW_INTERVALS[level]
            next_review = now + interval

            if name in self.review_items:
                # Update existing
                item = self.review_items[name]
                item.mastery_score = mastery
                item.last_reviewed = now.isoformat()
                item.next_review = next_review.isoformat()
                item.review_count += 1
            else:
                # Add new
                desc = ""
                if hasattr(state, "description"):
                    desc = state.description
                self.review_items[name] = ReviewItem(
                    concept_name=name,
                    concept_description=desc,
                    mastery_score=mastery,
                    last_reviewed=now.isoformat(),
                    next_review=next_review.isoformat(),
                )

    def get_due_items(self) -> list[ReviewItem]:
        """Get all items that are due for review."""
        return [item for item in self.review_items.values() if item.is_due]

    def get_weak_items(self, threshold: float = 0.7) -> list[ReviewItem]:
        """Get items below a mastery threshold."""
        return [
            item for item in self.review_items.values()
            if item.mastery_score < threshold
        ]

    def get_all_items_sorted(self) -> list[ReviewItem]:
        """Get all items sorted by mastery (weakest first)."""
        items = list(self.review_items.values())
        items.sort(key=lambda x: x.mastery_score)
        return items

    def to_dict(self) -> dict:
        """Serialize for persistence."""
        return {
            "review_items": {
                name: item.to_dict()
                for name, item in self.review_items.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpacedRepetitionEngine":
        """Deserialize from dictionary."""
        engine = cls()
        items_data = data.get("review_items", {})
        for name, item_data in items_data.items():
            engine.review_items[name] = ReviewItem.from_dict(item_data)
        return engine
