-- Supabase setup for the live shared leaderboard.
--
-- Run this once in your Supabase project's SQL editor
-- (Dashboard -> SQL Editor -> New query -> paste -> Run).
--
-- Then set SUPABASE_URL and SUPABASE_KEY (the public "anon" key) in your
-- Streamlit secrets / .env. Without them, the app falls back to the offline
-- code-passing leaderboard automatically.

create table if not exists public.quiz_scores (
    id            bigint generated always as identity primary key,
    quiz_id       text        not null,
    player        text        not null,
    score_correct integer     not null,
    score_total   integer     not null,
    percentage    real        not null,
    time_seconds  integer     not null default 0,
    created_at    timestamptz not null default now()
);

-- Fast lookups per quiz.
create index if not exists quiz_scores_quiz_id_idx
    on public.quiz_scores (quiz_id);

-- Row Level Security: this is a public, anonymous leaderboard, so allow anyone
-- (the anon role) to read and insert scores. Scores cannot be updated/deleted
-- from the client.
alter table public.quiz_scores enable row level security;

drop policy if exists "public read scores" on public.quiz_scores;
create policy "public read scores"
    on public.quiz_scores
    for select
    using (true);

drop policy if exists "public insert scores" on public.quiz_scores;
create policy "public insert scores"
    on public.quiz_scores
    for insert
    with check (true);
