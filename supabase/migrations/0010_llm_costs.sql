-- 0010_llm_costs.sql · OpenAI money spent outside runs, so the monthly budget sees it (C-008)
-- Runs and the extractor already record their cost on each response. The deeper free
-- diagnostic (C-008) also calls gpt-5-nano, even when the PDF is not uploaded, so its cost
-- goes here and motor/presupuesto.month_usage adds it to the month. Service role only.

create table public.llm_costs (
    id bigint generated always as identity primary key,
    kind text not null check (kind in ('diagnostic_reasons')),
    market_id bigint references public.markets (id) on delete set null,
    clinic_id bigint references public.clinics (id) on delete set null,
    month date check (month is null or extract(day from month) = 1),
    model text not null,
    calls int not null check (calls >= 0),
    cost_usd numeric(10, 6) not null check (cost_usd >= 0),
    created_at timestamptz not null default now()
);

alter table public.llm_costs enable row level security;
revoke all on public.llm_costs from anon, authenticated;
