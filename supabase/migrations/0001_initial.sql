-- 0001_initial.sql · visible-ia initial schema (C1-T03)
-- Data model: docs/04-arquitectura/arquitectura.md ("Modelo de datos").
-- Table names are in English (code convention); the comment shows the name used in the docs.
-- RLS is enabled on EVERY table and no policy is created here: only the service_role
-- (CLI and GitHub Actions) can read/write. Policies come in later migrations (C6, C7, C10).

-- rubro
create table public.categories (
    code text primary key check (code in ('IMP', 'EDE', 'MES', 'DER')),
    name text not null
);

-- plantilla
create table public.templates (
    id text primary key,                                  -- e.g. IMP-01
    category_code text not null references public.categories (code),
    form char(1) not null check (form in ('M', 'R', 'C', 'P')),
    text text not null check (position('{d}' in text) > 0),
    origin text,                                          -- Q01..Q30 or 'Nueva'
    version int not null default 1,
    active boolean not null default true
);

-- mercado
create table public.markets (
    id bigint generated always as identity primary key,
    category_code text not null references public.categories (code),
    district text not null check (district in ('Miraflores', 'San Isidro', 'Surco')),
    question_set_version int not null default 1,
    active boolean not null default true,
    created_at timestamptz not null default now(),
    unique (category_code, district)
);

-- pregunta
create table public.questions (
    id bigint generated always as identity primary key,
    market_id bigint not null references public.markets (id) on delete cascade,
    template_id text not null references public.templates (id),
    text text not null,
    version int not null default 1,
    created_at timestamptz not null default now(),
    unique (market_id, template_id, version)
);

-- clinica
create table public.clinics (
    id bigint generated always as identity primary key,
    name text not null,
    address text,
    district text,
    rating numeric(2, 1) check (rating between 0 and 5),
    review_count int check (review_count >= 0),
    website text,
    instagram text,
    maps_url text unique,
    data_date date,                                       -- date of rating/review_count
    created_at timestamptz not null default now()
);

-- clinica_mercado
create table public.clinic_markets (
    clinic_id bigint not null references public.clinics (id) on delete cascade,
    market_id bigint not null references public.markets (id) on delete cascade,
    primary key (clinic_id, market_id)
);

-- alias
create table public.aliases (
    id bigint generated always as identity primary key,
    clinic_id bigint not null references public.clinics (id) on delete cascade,
    alias text not null
);
create unique index aliases_clinic_alias_uq on public.aliases (clinic_id, lower(alias));

-- corrida
create table public.runs (
    id bigint generated always as identity primary key,
    market_id bigint not null references public.markets (id),
    month date not null check (extract(day from month) = 1),
    kind text not null check (kind in ('api', 'manual')),
    status text not null default 'pending'
        check (status in ('pending', 'running', 'incomplete', 'complete', 'reviewed')),
    estimated_cost_usd numeric(10, 4),
    actual_cost_usd numeric(10, 4),
    forced boolean not null default false,               -- budget override confirmed by operator
    created_at timestamptz not null default now()
);

-- respuesta
create table public.responses (
    id bigint generated always as identity primary key,
    run_id bigint not null references public.runs (id) on delete cascade,
    question_id bigint not null references public.questions (id),
    surface text not null check (surface in
        ('chatgpt_api', 'google_ai_mode', 'chatgpt_app_manual', 'gemini_app_manual')),
    repetition int not null check (repetition >= 1),
    provider text,
    model text,
    text text,                                            -- purged after 12 months (ADR-002)
    raw jsonb,                                            -- purged after 12 months (ADR-002)
    cost_usd numeric(10, 6),
    created_at timestamptz not null default now(),
    purge_after date not null default (((now() at time zone 'America/Lima')::date + interval '12 months')::date),
    unique (run_id, question_id, surface, repetition)
);

-- mencion
create table public.mentions (
    id bigint generated always as identity primary key,
    response_id bigint not null references public.responses (id) on delete cascade,
    position int not null check (position >= 1),
    raw_name text not null,
    clinic_id bigint references public.clinics (id),     -- null = new clinic
    status text not null default 'auto'
        check (status in ('auto', 'corrected', 'discarded', 'review')),
    extractor_version text,
    created_at timestamptz not null default now()
);

-- fuente
create table public.sources (
    id bigint generated always as identity primary key,
    response_id bigint not null references public.responses (id) on delete cascade,
    url text not null,
    domain text not null,
    source_type text not null default 'other' check (source_type in
        ('google_profile', 'doctoralia', 'own_website', 'social', 'directory', 'press', 'other'))
);

-- puntaje_mensual
create table public.monthly_scores (
    id bigint generated always as identity primary key,
    market_id bigint not null references public.markets (id),
    month date not null check (extract(day from month) = 1),
    clinic_id bigint not null references public.clinics (id),
    surface text not null check (surface in ('chatgpt_api', 'google_ai_mode', 'combined')),
    n_responses int not null,
    appearances int not null,
    presence_index numeric(5, 2) not null,               -- 0..100
    ci_low numeric(5, 2),
    ci_high numeric(5, 2),
    avg_position numeric(5, 2),
    mention_share numeric(5, 2),
    change text check (change in ('up', 'down', 'no_clear_change', 'first_month')),
    window3_index numeric(5, 2),
    window3_ci_low numeric(5, 2),
    window3_ci_high numeric(5, 2),
    detectable_diff numeric(5, 2),
    created_at timestamptz not null default now(),
    unique (market_id, month, clinic_id, surface)
);

-- cliente
create table public.clients (
    id bigint generated always as identity primary key,
    kind text not null check (kind in ('clinic', 'agency')),
    name text not null,
    contact_email text,
    contact_phone text,
    parent_agency_id bigint references public.clients (id),
    logo_path text,
    brand_colors jsonb,
    status text not null default 'active' check (status in ('active', 'paused', 'ended')),
    created_at timestamptz not null default now(),
    ended_at timestamptz
);

-- sede
create table public.sites (
    id bigint generated always as identity primary key,
    client_id bigint not null references public.clients (id) on delete cascade,
    clinic_id bigint not null references public.clinics (id),
    market_id bigint not null references public.markets (id),
    active_from date not null default current_date,
    active_to date
);

-- usuario
create table public.app_users (
    id uuid primary key references auth.users (id) on delete cascade,
    client_id bigint not null references public.clients (id) on delete cascade,
    role text not null check (role in ('clinic', 'agency')),
    created_at timestamptz not null default now()
);

-- tarea
create table public.tasks (
    id bigint generated always as identity primary key,
    site_id bigint not null references public.sites (id) on delete cascade,
    code text not null,
    status text not null default 'pending' check (status in ('pending', 'done')),
    updated_at timestamptz not null default now(),
    unique (site_id, code)
);

-- informe
create table public.reports (
    id bigint generated always as identity primary key,
    kind text not null check (kind in ('diagnostic', 'monthly')),
    clinic_id bigint references public.clinics (id),
    site_id bigint references public.sites (id),
    month date,
    pdf_path text not null,
    brand text not null default 'visible-ia' check (brand in ('visible-ia', 'agency')),
    created_at timestamptz not null default now(),
    check (clinic_id is not null or site_id is not null)
);

-- prospecto
create table public.prospects (
    id bigint generated always as identity primary key,
    name text not null,
    clinic_name text not null,
    district text,
    category_code text references public.categories (code),
    contact text not null,
    utm jsonb,
    consent boolean not null check (consent),            -- form cannot be sent without consent
    consent_at timestamptz not null default now(),
    status text not null default 'new' check (status in ('new', 'contacted', 'report_sent', 'client', 'discarded')),
    do_not_contact boolean not null default false,
    seen boolean not null default false,
    clinic_id bigint references public.clinics (id),
    created_at timestamptz not null default now()
);

-- pago
create table public.payments (
    id bigint generated always as identity primary key,
    client_id bigint not null references public.clients (id),
    period date not null check (extract(day from period) = 1),
    amount_pen numeric(10, 2) not null check (amount_pen > 0),
    method text not null check (method in ('link', 'yape', 'transfer', 'subscription')),
    paid_on date not null,
    reference text,
    created_at timestamptz not null default now()
);

-- latido
create table public.heartbeats (
    id bigint generated always as identity primary key,
    project text not null check (project in ('dev', 'prod')),
    created_at timestamptz not null default now()
);

-- Row Level Security on every table (no policies yet: deny all except service_role)
alter table public.categories enable row level security;
alter table public.templates enable row level security;
alter table public.markets enable row level security;
alter table public.questions enable row level security;
alter table public.clinics enable row level security;
alter table public.clinic_markets enable row level security;
alter table public.aliases enable row level security;
alter table public.runs enable row level security;
alter table public.responses enable row level security;
alter table public.mentions enable row level security;
alter table public.sources enable row level security;
alter table public.monthly_scores enable row level security;
alter table public.clients enable row level security;
alter table public.sites enable row level security;
alter table public.app_users enable row level security;
alter table public.tasks enable row level security;
alter table public.reports enable row level security;
alter table public.prospects enable row level security;
alter table public.payments enable row level security;
alter table public.heartbeats enable row level security;

-- Seed: the 4 categories (idempotent)
insert into public.categories (code, name) values
    ('IMP', 'Implantología'),
    ('EDE', 'Estética dental'),
    ('MES', 'Medicina estética'),
    ('DER', 'Dermatología')
on conflict (code) do nothing;
