-- 0002_runs_resume.sql · what a run asked for, so it can be resumed (C3-T04, HU-04)
-- A run remembers its question bank version, surfaces and repetitions; `failures` keeps the
-- calls that failed in the last attempt (PRD: "incompleta, con la lista de lo que falló").

alter table public.runs
    add column question_set_version int,
    add column surfaces text[] not null default array['chatgpt_api', 'google_ai_mode'],
    add column repetitions int not null default 3 check (repetitions >= 1),
    add column failures jsonb not null default '[]'::jsonb,
    add column started_at timestamptz,
    add column finished_at timestamptz;

-- The surface answered but without an AI answer (e.g. Google showed no AI Mode block).
alter table public.responses
    add column no_answer boolean not null default false;
