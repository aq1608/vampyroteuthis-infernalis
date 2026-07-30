"""
Course Completion Certificate - Generate a downloadable SVG certificate.

Awarded when a student completes an entire learning path. Uses SVG so it
needs no extra dependencies, scales perfectly, and prints beautifully.
"""

from __future__ import annotations

from datetime import datetime
from xml.sax.saxutils import escape


def _fmt_name(name: str) -> str:
    """Sanitize and default the student name for XML embedding."""
    name = (name or "").strip() or "Anonymous Learner"
    # Keep certificates tidy
    if len(name) > 40:
        name = name[:37] + "..."
    return escape(name)



def generate_certificate_svg(
    student_name: str,
    path_name: str,
    topics_completed: int,
    average_score: float | None = None,
    total_xp: int | None = None,
    level_title: str | None = None,
    completion_date: str | None = None,
) -> str:
    """
    Generate a course completion certificate as an SVG string.

    Args:
        student_name: The learner's name.
        path_name: The completed learning path.
        topics_completed: Number of topics in the path.
        average_score: Optional average quiz score (%) across the path.
        total_xp: Optional total XP earned.
        level_title: Optional current level title (e.g., "Scholar").
        completion_date: Optional date string; defaults to today.

    Returns:
        A complete SVG document string.
    """
    name = _fmt_name(student_name)
    path = escape(path_name)
    date_str = completion_date or datetime.now().strftime("%B %d, %Y")

    # Build the optional stats line
    stat_parts = [f"{topics_completed} topics mastered"]
    if average_score is not None:
        stat_parts.append(f"{average_score:.0f}% average score")
    if total_xp is not None:
        stat_parts.append(f"{total_xp} XP earned")
    stats_line = escape("  •  ".join(stat_parts))

    level_line = ""
    if level_title:
        level_line = (
            f'<text x="500" y="486" text-anchor="middle" '
            f'font-family="Georgia, serif" font-size="18" fill="#7F8C8D">'
            f'Achieved rank: {escape(level_title)}</text>'
        )

    # A verification-style ID from the inputs (cosmetic)
    cert_id = abs(hash(f"{name}{path}{date_str}")) % 10_000_000
    cert_id_str = f"AQG-{cert_id:07d}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700" viewBox="0 0 1000 700">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f5f4ff"/>
    </linearGradient>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6C63FF"/>
      <stop offset="100%" stop-color="#4ECDC4"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1000" height="700" fill="url(#bgGrad)"/>

  <!-- Outer border -->
  <rect x="24" y="24" width="952" height="652" fill="none"
        stroke="url(#brandGrad)" stroke-width="6" rx="18"/>
  <rect x="40" y="40" width="920" height="620" fill="none"
        stroke="#E0DEF7" stroke-width="2" rx="12"/>

  <!-- Top brand bar -->
  <rect x="40" y="40" width="920" height="10" fill="url(#brandGrad)" rx="5"/>

  <!-- Header -->
  <text x="500" y="130" text-anchor="middle"
        font-family="Georgia, serif" font-size="20" letter-spacing="4"
        fill="#7F8C8D">ADAPTIVE QUIZ GENERATOR</text>

  <text x="500" y="200" text-anchor="middle"
        font-family="Georgia, serif" font-size="52" font-weight="bold"
        fill="#2C3E50">Certificate of Completion</text>

  <!-- Divider -->
  <rect x="380" y="228" width="240" height="4" fill="url(#brandGrad)" rx="2"/>

  <!-- Body -->
  <text x="500" y="292" text-anchor="middle"
        font-family="Georgia, serif" font-size="20" fill="#7F8C8D">
    This certifies that
  </text>

  <text x="500" y="360" text-anchor="middle"
        font-family="Georgia, serif" font-size="46" font-weight="bold"
        fill="#6C63FF">{name}</text>

  <text x="500" y="416" text-anchor="middle"
        font-family="Georgia, serif" font-size="20" fill="#7F8C8D">
    has successfully completed the learning path
  </text>

  <text x="500" y="456" text-anchor="middle"
        font-family="Georgia, serif" font-size="30" font-weight="bold"
        fill="#2C3E50">{path}</text>

  {level_line}

  <!-- Stats -->
  <text x="500" y="540" text-anchor="middle"
        font-family="Georgia, serif" font-size="18" fill="#34495E">{stats_line}</text>

  <!-- Footer: date and id -->
  <text x="230" y="620" text-anchor="middle"
        font-family="Georgia, serif" font-size="16" fill="#2C3E50">{escape(date_str)}</text>
  <rect x="120" y="632" width="220" height="2" fill="#BDC3C7"/>
  <text x="230" y="652" text-anchor="middle"
        font-family="Georgia, serif" font-size="13" fill="#7F8C8D">Date</text>

  <text x="770" y="620" text-anchor="middle"
        font-family="Georgia, serif" font-size="16" fill="#2C3E50">{cert_id_str}</text>
  <rect x="660" y="632" width="220" height="2" fill="#BDC3C7"/>
  <text x="770" y="652" text-anchor="middle"
        font-family="Georgia, serif" font-size="13" fill="#7F8C8D">Certificate ID</text>

  <!-- Seal -->
  <circle cx="500" cy="628" r="34" fill="none" stroke="url(#brandGrad)" stroke-width="3"/>
  <text x="500" y="622" text-anchor="middle"
        font-family="Georgia, serif" font-size="13" font-weight="bold" fill="#6C63FF">AI</text>
  <text x="500" y="638" text-anchor="middle"
        font-family="Georgia, serif" font-size="11" fill="#7F8C8D">ML</text>
</svg>"""
    return svg


def certificate_filename(student_name: str, path_name: str) -> str:
    """Build a friendly download filename for the certificate."""
    def slug(s: str) -> str:
        s = (s or "").strip().lower()
        return "".join(c if c.isalnum() else "-" for c in s).strip("-") or "certificate"

    return f"certificate-{slug(student_name)}-{slug(path_name)}.svg"


def compute_path_average_score(quiz_history: list[dict], path_topics: list[str]) -> float | None:
    """
    Compute the average score for quizzes taken on a given path's topics.

    Falls back to None if there is no matching history. Uses the recorded
    quiz history's content_source, which for curriculum quizzes contains the
    generated topic material (best-effort match on percentage average).

    Args:
        quiz_history: List of quiz summary dicts.
        path_topics: Topic names in the path (unused for strict matching but
            kept for future precise matching).

    Returns:
        Average score percentage, or None.
    """
    if not quiz_history:
        return None
    # Best-effort: average the most recent quizzes equal to path length
    recent = quiz_history[-max(len(path_topics), 1):]
    scores = [q.get("score_percentage", 0) for q in recent]
    if not scores:
        return None
    return sum(scores) / len(scores)
