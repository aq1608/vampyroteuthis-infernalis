"""
Learning Analytics - Track improvement over time and predict retention.

Provides:
- Performance trend analysis across quiz sessions
- Predicted retention curves per concept
- Study pattern insights (best times, optimal session length)
- Strengths/weaknesses analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math


# Ebbinghaus forgetting curve constant
FORGETTING_RATE = 0.5  # Higher = faster forgetting


@dataclass
class AnalyticsEngine:
    """Tracks and analyzes learning performance over time."""

    # Session history: list of {timestamp, score, concepts_tested, duration}
    sessions: list = field(default_factory=list)
    # Per-concept performance over time: concept -> [{timestamp, mastery, attempts}]
    concept_timeline: dict = field(default_factory=dict)
    # Study patterns
    study_times: list = field(default_factory=list)  # List of hour-of-day values

    def record_session(
        self,
        score_percentage: float,
        concepts_tested: list[str],
        concept_masteries: dict,
        duration_seconds: int = 0,
    ):
        """Record a completed study session."""
        now = datetime.now()

        self.sessions.append({
            "timestamp": now.isoformat(),
            "score": score_percentage,
            "concepts_tested": concepts_tested,
            "duration": duration_seconds,
        })

        # Track study time
        self.study_times.append(now.hour)

        # Update concept timeline
        for concept, mastery in concept_masteries.items():
            if concept not in self.concept_timeline:
                self.concept_timeline[concept] = []
            self.concept_timeline[concept].append({
                "timestamp": now.isoformat(),
                "mastery": mastery,
            })



    def get_performance_trend(self) -> list[dict]:
        """Get score trend over last N sessions."""
        return [
            {
                "session": i + 1,
                "score": s["score"],
                "timestamp": s["timestamp"][:10],
            }
            for i, s in enumerate(self.sessions[-20:])
        ]

    def get_improvement_rate(self) -> float:
        """Calculate improvement rate as % change over recent sessions."""
        if len(self.sessions) < 2:
            return 0.0
        recent = self.sessions[-5:]
        if len(recent) < 2:
            return 0.0
        first_avg = recent[0]["score"]
        last_avg = recent[-1]["score"]
        return last_avg - first_avg

    def predict_retention(self, concept: str, hours_from_now: int = 24) -> float:
        """
        Predict retention for a concept using Ebbinghaus forgetting curve.

        R = e^(-t/S) where t=time, S=memory strength (based on reviews)
        """
        timeline = self.concept_timeline.get(concept, [])
        if not timeline:
            return 0.0

        # Memory strength increases with successful reviews
        num_reviews = len(timeline)
        latest_mastery = timeline[-1]["mastery"]

        # Strength is based on mastery and review count
        strength = latest_mastery * (1 + math.log(num_reviews + 1))

        # Forgetting curve: R = e^(-t/S)
        retention = math.exp(
            -hours_from_now * FORGETTING_RATE / max(strength, 0.1)
        )
        return min(max(retention, 0.0), 1.0)

    def get_retention_forecast(self, concepts: list[str]) -> list[dict]:
        """Get predicted retention for each concept at various time points."""
        forecast = []
        time_points = [1, 6, 12, 24, 48, 72, 168]  # hours

        for concept in concepts:
            concept_forecast = {"concept": concept, "predictions": []}
            for hours in time_points:
                retention = self.predict_retention(concept, hours)
                concept_forecast["predictions"].append({
                    "hours": hours,
                    "retention": retention * 100,
                })
            forecast.append(concept_forecast)
        return forecast

    def get_optimal_study_time(self) -> str:
        """Determine the best time of day to study based on patterns."""
        if not self.study_times:
            return "No data yet"

        # Find hour with best performance
        hour_scores = {}
        for i, session in enumerate(self.sessions):
            if i < len(self.study_times):
                hour = self.study_times[i]
                if hour not in hour_scores:
                    hour_scores[hour] = []
                hour_scores[hour].append(session["score"])

        if not hour_scores:
            return "No data yet"

        best_hour = max(
            hour_scores,
            key=lambda h: sum(hour_scores[h]) / len(hour_scores[h])
        )

        # Format as readable time
        if best_hour < 12:
            return f"{best_hour}:00 AM"
        elif best_hour == 12:
            return "12:00 PM"
        else:
            return f"{best_hour - 12}:00 PM"

    def get_strengths_weaknesses(self) -> dict:
        """Analyze concepts to identify strengths and weaknesses."""
        strengths = []
        weaknesses = []

        for concept, timeline in self.concept_timeline.items():
            if not timeline:
                continue
            latest = timeline[-1]["mastery"]
            if latest >= 0.8:
                strengths.append({"concept": concept, "mastery": latest})
            elif latest < 0.6:
                weaknesses.append({"concept": concept, "mastery": latest})

        strengths.sort(key=lambda x: x["mastery"], reverse=True)
        weaknesses.sort(key=lambda x: x["mastery"])

        return {"strengths": strengths[:5], "weaknesses": weaknesses[:5]}

    def get_study_streak_days(self) -> int:
        """Calculate consecutive days studied."""
        if not self.sessions:
            return 0

        dates = set()
        for session in self.sessions:
            date_str = session["timestamp"][:10]
            dates.add(date_str)

        today = datetime.now().date()
        streak = 0
        check_date = today

        while check_date.isoformat() in dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def to_dict(self) -> dict:
        """Serialize for persistence."""
        return {
            "sessions": self.sessions,
            "concept_timeline": self.concept_timeline,
            "study_times": self.study_times,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalyticsEngine":
        """Deserialize from dictionary."""
        engine = cls()
        engine.sessions = data.get("sessions", [])
        engine.concept_timeline = data.get("concept_timeline", {})
        engine.study_times = data.get("study_times", [])
        return engine
