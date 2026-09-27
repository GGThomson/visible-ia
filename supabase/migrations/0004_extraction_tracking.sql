-- 0004_extraction_tracking.sql · which answers were extracted, how and at what cost (C4-T04)
-- `extract` only processes answers without extracted_at, and the extractor's cost counts in
-- the monthly OpenAI budget (HU-05).

alter table public.responses
    add column extracted_at timestamptz,
    add column extractor_version text,
    add column extraction_cost_usd numeric(10, 6);

-- Review audit: who/what changed a mention (optional note, e.g. "unida con 123").
alter table public.mentions
    add column note text,
    add column updated_at timestamptz;
