"""
Gamification - Points, streaks, badges, and level system.

Tracks XP, awards badges for achievements, maintains streaks,
and provides a level progression system to keep learners engaged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from datetime import datetime


# XP rewards
XP_CORRECT_BEGINNER = 10
XP_CORRECT_INTERMEDIATE = 20
XP_CORRECT_ADVANCED = 35
XP_STREAK_BONUS = 5  # Extra XP per streak count
XP_PERFECT_CONCEPT = 50  # Bonus for 100% on a concept

# Level thresholds (cumulative XP needed)
LEVELS = [
    {"level": 1, "title": "Novice", "xp_required": 0},
    {"level": 2, "title": "Learner", "xp_required": 50},
    {"level": 3, "title": "Student", "xp_required": 150},
    {"level": 4, "title": "Scholar", "xp_required": 300},
    {"level": 5, "title": "Expert", "xp_required": 500},
    {"level": 6, "title": "Master", "xp_required": 800},
    {"level": 7, "title": "Sage", "xp_required": 1200},
    {"level": 8, "title": "Genius", "xp_required": 1800},
]

# Badge definitions
BADGES = {
    "first_quiz": {
        "name": "First Steps",
        "icon": "baby",
        "description": "Complete your first quiz",
        "condition": "complete_quiz",
    },
    "streak_3": {
        "name": "On Fire",
        "icon": "fire",
        "description": "Get 3 correct in a row",
        "condition": "streak_3",
    },
    "streak_5": {
        "name": "Unstoppable",
        "icon": "zap",
        "description": "Get 5 correct in a row",
        "condition": "streak_5",
    },
    "streak_10": {
        "name": "Legendary",
        "icon": "star2",
        "description": "Get 10 correct in a row",
        "condition": "streak_10",
    },
    "perfect_concept": {
        "name": "Perfectionist",
        "icon": "100",
        "description": "Get 100% on any concept",
        "condition": "perfect_concept",
    },
    "all_mastered": {
        "name": "Master of All",
        "icon": "trophy",
        "description": "Master all concepts in a quiz (80%+)",
        "condition": "all_mastered",
    },
    "speed_demon": {
        "name": "Speed Demon",
        "icon": "racing_car",
        "description": "Answer 5 questions under the time limit in timer mode",
        "condition": "speed_5",
    },
    "polyglot": {
        "name": "Polyglot",
        "icon": "globe_with_meridians",
        "description": "Complete a quiz in a non-English language",
        "condition": "non_english_quiz",
    },
    "level_5": {
        "name": "Expert Status",
        "icon": "mortar_board",
        "description": "Reach Level 5",
        "condition": "reach_level_5",
    },
    "comeback": {
        "name": "Comeback Kid",
        "icon": "muscle",
        "description": "Improve a weak concept from below 50% to above 80%",
        "condition": "comeback",
    },
}

# Emoji mapping for badges
BADGE_EMOJIS = {
    "baby": "\U0001F476",
    "fire": "\U0001F525",
    "zap": "\u26A1",
    "star2": "\U0001F31F",
    "100": "\U0001F4AF",
    "trophy": "\U0001F3C6",
    "racing_car": "\U0001F3CE\uFE0F",
    "globe_with_meridians": "\U0001F310",
    "mortar_board": "\U0001F393",
    "muscle": "\U0001F4AA",
}


@dataclass
class GamificationEngine:
    """Manages XP, levels, streaks, and badges."""

    total_xp: int = 0
    current_streak: int = 0
    best_streak: int = 0
    badges_earned: list = field(default_factory=list)  # List of badge IDs
    quizzes_completed: int = 0
    total_questions_answered: int = 0
    total_correct: int = 0
    speed_answers: int = 0  # Answers within time limit in timer mode
    has_non_english_quiz: bool = False
    concept_history: dict = field(default_factory=dict)  # concept -> {prev_mastery, current_mastery}

    @property
    def current_level(self) -> dict:
        """Get the current level based on total XP."""
        current = LEVELS[0]
        for level in LEVELS:
            if self.total_xp >= level["xp_required"]:
                current = level
            else:
                break
        return current

    @property
    def next_level(self) -> dict | None:
        """Get the next level info, or None if max level."""
        current_idx = self.current_level["level"] - 1
        if current_idx + 1 < len(LEVELS):
            return LEVELS[current_idx + 1]
        return None

    @property
    def xp_progress(self) -> float:
        """Get progress toward next level (0.0 to 1.0)."""
        current = self.current_level
        next_lvl = self.next_level
        if not next_lvl:
            return 1.0
        xp_in_level = self.total_xp - current["xp_required"]
        xp_needed = next_lvl["xp_required"] - current["xp_required"]
        return min(xp_in_level / xp_needed, 1.0) if xp_needed > 0 else 1.0

    def award_xp(self, difficulty: str, is_correct: bool) -> int:
        """
        Award XP for an answer and return the amount awarded.

        Args:
            difficulty: Question difficulty level.
            is_correct: Whether the answer was correct.

        Returns:
            Amount of XP awarded.
        """
        if not is_correct:
            self.current_streak = 0
            self.total_questions_answered += 1
            return 0

        # Base XP by difficulty
        xp_map = {
            "beginner": XP_CORRECT_BEGINNER,
            "intermediate": XP_CORRECT_INTERMEDIATE,
            "advanced": XP_CORRECT_ADVANCED,
        }
        xp = xp_map.get(difficulty, XP_CORRECT_BEGINNER)

        # Streak bonus
        self.current_streak += 1
        self.best_streak = max(self.best_streak, self.current_streak)
        xp += self.current_streak * XP_STREAK_BONUS

        self.total_xp += xp
        self.total_correct += 1
        self.total_questions_answered += 1

        # Check for new badges
        self._check_streak_badges()
        self._check_level_badges()

        return xp

    def complete_quiz(self, concept_masteries: dict | None = None):
        """
        Record quiz completion and check for badges.

        Args:
            concept_masteries: Dict of concept_name -> mastery_score (0.0-1.0)
        """
        self.quizzes_completed += 1
        self._earn_badge("first_quiz")

        if concept_masteries:
            # Check for perfect concept
            for name, mastery in concept_masteries.items():
                if mastery >= 1.0:
                    self._earn_badge("perfect_concept")
                    self.total_xp += XP_PERFECT_CONCEPT

                # Check for comeback
                prev = self.concept_history.get(name, {}).get("prev_mastery", 0)
                if prev < 0.5 and mastery >= 0.8:
                    self._earn_badge("comeback")

                # Update history
                if name not in self.concept_history:
                    self.concept_history[name] = {}
                self.concept_history[name]["prev_mastery"] = mastery

            # Check if all mastered
            if all(m >= 0.8 for m in concept_masteries.values()):
                self._earn_badge("all_mastered")

    def record_timed_answer(self):
        """Record that a question was answered within the time limit."""
        self.speed_answers += 1
        if self.speed_answers >= 5:
            self._earn_badge("speed_demon")

    def record_non_english_quiz(self):
        """Record that a quiz was completed in a non-English language."""
        self.has_non_english_quiz = True
        self._earn_badge("polyglot")

    def _check_streak_badges(self):
        """Check and award streak-based badges."""
        if self.current_streak >= 3:
            self._earn_badge("streak_3")
        if self.current_streak >= 5:
            self._earn_badge("streak_5")
        if self.current_streak >= 10:
            self._earn_badge("streak_10")

    def _check_level_badges(self):
        """Check and award level-based badges."""
        if self.current_level["level"] >= 5:
            self._earn_badge("level_5")

    def _earn_badge(self, badge_id: str):
        """Earn a badge if not already earned."""
        if badge_id not in self.badges_earned:
            self.badges_earned.append(badge_id)

    def get_badge_info(self, badge_id: str) -> dict:
        """Get full badge info including emoji."""
        badge = BADGES.get(badge_id, {})
        emoji = BADGE_EMOJIS.get(badge.get("icon", ""), "")
        return {
            "id": badge_id,
            "name": badge.get("name", "Unknown"),
            "emoji": emoji,
            "description": badge.get("description", ""),
        }

    def get_all_badges_status(self) -> list[dict]:
        """Get all badges with earned/locked status."""
        result = []
        for badge_id, badge_info in BADGES.items():
            emoji = BADGE_EMOJIS.get(badge_info.get("icon", ""), "")
            result.append({
                "id": badge_id,
                "name": badge_info["name"],
                "emoji": emoji,
                "description": badge_info["description"],
                "earned": badge_id in self.badges_earned,
            })
        return result

    def to_dict(self) -> dict:
        """Serialize to dictionary for persistence."""
        return {
            "total_xp": self.total_xp,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "badges_earned": self.badges_earned,
            "quizzes_completed": self.quizzes_completed,
            "total_questions_answered": self.total_questions_answered,
            "total_correct": self.total_correct,
            "speed_answers": self.speed_answers,
            "has_non_english_quiz": self.has_non_english_quiz,
            "concept_history": self.concept_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GamificationEngine":
        """Deserialize from dictionary."""
        engine = cls()
        engine.total_xp = data.get("total_xp", 0)
        engine.current_streak = data.get("current_streak", 0)
        engine.best_streak = data.get("best_streak", 0)
        engine.badges_earned = data.get("badges_earned", [])
        engine.quizzes_completed = data.get("quizzes_completed", 0)
        engine.total_questions_answered = data.get("total_questions_answered", 0)
        engine.total_correct = data.get("total_correct", 0)
        engine.speed_answers = data.get("speed_answers", 0)
        engine.has_non_english_quiz = data.get("has_non_english_quiz", False)
        engine.concept_history = data.get("concept_history", {})
        return engine
