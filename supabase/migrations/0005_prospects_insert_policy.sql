-- 0005_prospects_insert_policy.sql · the landing form may only INSERT prospects (C6-T03, HU-26)
-- The anon key is public by design (it is in the web page): RLS is what protects the data.
-- anon can insert a new request with consent and nothing else: it cannot read, change or
-- delete prospects, nor touch the internal fields (status, seen, clinic, do-not-contact).

revoke select, update, delete on public.prospects from anon;
grant insert on public.prospects to anon;

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
    );
