-- 0003_google_manual_surface.sql · manual samples of Google AI Mode (C3-T05, HU-06)
-- Decided by the Director on 2026-09-26: the phase-1 sample includes Google AI Mode answers
-- taken by hand in the browser. Like the other manual surfaces, it never enters the index
-- (monthly_scores keeps only chatgpt_api, google_ai_mode and combined).

alter table public.responses drop constraint responses_surface_check;
alter table public.responses add constraint responses_surface_check check (surface in (
    'chatgpt_api', 'google_ai_mode',
    'chatgpt_app_manual', 'gemini_app_manual', 'google_ai_mode_manual'
));
