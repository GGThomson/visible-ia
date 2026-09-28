-- 0009_prospects_consent_version.sql · which privacy policy version the visitor accepted (C9b)
-- Proof of consent (Ley 29733): consent_at already records when; this records which version
-- of web/privacidad.html (its date, e.g. '2026-09-28'). Nullable for now: the landing live in
-- production today does not send it yet. Once the new landing is published, a later migration
-- makes it required.

alter table public.prospects
    add column consent_version text
        check (consent_version is null or consent_version ~ '^\d{4}-\d{2}-\d{2}$');

drop policy prospects_anon_insert_only on public.prospects;

create policy prospects_anon_insert_only on public.prospects
    for insert to anon
    with check (
        consent
        and status = 'new'
        and seen = false
        and do_not_contact = false
        and clinic_id is null
        and char_length(name) between 2 and 120
        and char_length(clinic_name) between 2 and 160
        and char_length(contact) between 6 and 160
        and (district is null or char_length(district) <= 60)
        and (utm is null or pg_column_size(utm) <= 2000)
        and consent_at between now() - interval '10 minutes' and now() + interval '1 minute'
        and (consent_version is null or char_length(consent_version) = 10)
    );
