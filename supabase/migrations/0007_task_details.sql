-- 0007_task_details.sql · prioritized checklist (C8-T03, HU-17)
-- Each task keeps its order for that site and the text shown in the panel and the monthly
-- report, taken from data/checklist.toml when the checklist is generated.

alter table public.tasks
    add column priority int not null default 100,
    add column title text,
    add column detail text;
