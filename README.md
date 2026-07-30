# Adaptive Quiz Generator

An AI-powered educational tool that generates personalized quizzes from any content, adapts difficulty based on your performance, and provides instant explanations when you get stuck.

**Built for the Prometheus July AI Challenge 2026.**

---

## The Problem

Students read textbooks passively and retain very little. Research shows that **active recall** (testing yourself) and **spaced repetition** (revisiting weak areas) are the most effective study techniques — but creating good practice questions is time-consuming.

## The Solution

Upload any study material — a PDF, pasted text, or just a topic — and the AI will:

1. **Extract key concepts** from your content
2. **Generate a personalized quiz** (multiple choice, true/false, fill-in-the-blank)
3. **Adapt difficulty in real-time** based on your answers
4. **Explain mistakes** clearly when you get something wrong
5. **Show you exactly where to focus** with a results dashboard
6. **Generate a study guide** targeting your weak areas
7. **Track your progress** with XP, levels, and badges

---

## Features

### Core
- **Multi-format input** — PDF upload, paste text, or enter any topic
- **AI-powered question generation** — Varied question types at multiple difficulties
- **Adaptive difficulty** — Gets harder when you're doing well, easier when you're struggling
- **Instant explanations** — Wrong answers trigger clear, helpful explanations
- **Concept-level tracking** — See mastery per concept, not just an overall score

### Gamification
- **XP System** — Earn points for correct answers, bonus for streaks and difficulty
- **8 Levels** — Progress from Novice to Genius
- **10 Badges** — Unlock achievements like "On Fire" (3-streak) and "Perfectionist" (100% on a concept)
- **Streaks** — Build consecutive correct answer streaks for bonus XP

### Learning Science
- **Spaced Repetition** — Weak concepts are scheduled for review based on forgetting curves
- **AI Study Guide** — Generate and download a focused study guide targeting weak areas
- **Progress Persistence** — Export/import your progress as JSON to continue later

### Quality of Life
- **Multi-language** — Generate quizzes in 12 languages (English, Spanish, French, German, etc.)
- **Timer Mode** — Optional live countdown per question for exam simulation
- **Dark Mode** — Toggle a dark theme from the sidebar
- **Accessibility** — High-contrast, dyslexia-friendly font, large text, and reduced-motion options
- **Collaborative quizzes** — Share a quiz code so others can take the exact same quiz
- **Leaderboards** — A live shared leaderboard (via Supabase) when configured, or an offline code-passing leaderboard otherwise
- **Beautiful UI** — Custom-styled with gradient branding, animations, and Plotly charts
- **Zero Cost** — Runs entirely on Gemini's free tier

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + Custom CSS |
| AI/LLM | Google Gemini 2.0 Flash (free tier) |
| PDF Parsing | pdfplumber |
| Charts | Plotly |
| Language | Python 3.9+ |

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- A free Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/aq1608/vampyroteuthis.git
cd vampyroteuthis

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

You can also enter your API key directly in the app sidebar.

### Optional: Live Shared Leaderboard (Supabase)

By default, shared-quiz leaderboards use an offline "code-passing" model (players
swap updated quiz codes). To get a **live, always-current shared leaderboard**
instead:

1. Create a free project at [supabase.com](https://supabase.com).
2. In the project's **SQL Editor**, run the script in
   [`supabase_schema.sql`](supabase_schema.sql) (creates the `quiz_scores` table
   and its public read/insert policies).
3. Add your credentials to `.env` (local) or Streamlit secrets (cloud):
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   ```
   Use the public **anon** key — Row Level Security keeps it safe for client use.

If these aren't set, the app automatically falls back to the offline leaderboard.

---

## Project Structure

```
vampyroteuthis/
├── app.py                          # Main Streamlit app with routing
├── quiz_engine/
│   ├── __init__.py                 # Module exports
│   ├── content_parser.py           # PDF/text parsing and chunking
│   ├── concept_extractor.py        # AI concept extraction (multi-lang)
│   ├── question_generator.py       # Quiz generation (multi-lang)
│   ├── adaptive_logic.py           # Difficulty state machine
│   ├── evaluator.py                # Answer evaluation + explanations
│   ├── gamification.py             # XP, levels, streaks, badges
│   ├── spaced_repetition.py        # Review scheduling
│   ├── persistence.py              # Progress export/import
│   └── study_guide.py              # AI study guide generation
├── ui/
│   ├── __init__.py                 # Module description
│   ├── styles.py                   # Custom CSS and UI components
│   ├── upload_page.py              # Content input + settings
│   ├── quiz_page.py                # Interactive quiz + timer
│   └── results_page.py             # Dashboard + exports
├── requirements.txt                # Dependencies
├── .env.example                    # API key template
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## How the Adaptive Logic Works

The quiz adapts to your performance using a state machine per concept:

- **2 correct in a row** on a concept -> difficulty increases
- **1 wrong answer** -> AI explains the concept, difficulty decreases
- **3 wrong on the same concept** -> flagged for review, moves on

Each concept is tracked independently for a personalized difficulty curve.

## Gamification System

| Action | XP Reward |
|--------|-----------|
| Correct (Beginner) | 10 XP |
| Correct (Intermediate) | 20 XP |
| Correct (Advanced) | 35 XP |
| Streak bonus | +5 XP per streak count |
| Perfect concept (100%) | +50 XP bonus |

## Spaced Repetition

After each quiz, concepts are scheduled for review based on mastery:
- Critical (<30%) -> Review in 5 minutes
- Weak (30-50%) -> Review in 1 hour
- Moderate (50-70%) -> Review in 6 hours
- Strong (70-90%) -> Review in 1 day
- Mastered (>90%) -> Review in 3 days

---

## Deployment

Deploy for free on:

- **[Streamlit Cloud](https://streamlit.io/cloud)** — Connect GitHub repo, deploy in one click
- **[Hugging Face Spaces](https://huggingface.co/spaces)** — Supports Streamlit natively
- **[Render](https://render.com)** — Free tier with 750 hours/month

---

## License

MIT
