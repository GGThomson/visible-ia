-- 0011_prospects_consent_version_required.sql · the policy version is now required (C9b)
-- The Eminia landing (web/app.js) sends consent_version on every request since it was
-- published (Director's OK, 28/09/2026). Apply only after that landing is live: the old one
-- did not send it. prospects had no rows without it when this was written.

alter table public.prospects
    alter column consent_version set not null;

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
        and char_length(consent_version) = 10
    );
