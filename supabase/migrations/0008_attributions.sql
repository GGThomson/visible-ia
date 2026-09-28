-- 0008_attributions.sql · patients who came "through the AI", per site and month (C9-T02, HU-25)
-- The clinic counts them with the intake question of the attribution kit and saves the number
-- in its panel; the monthly report shows it. It can only read and write its own sites
-- (private.my_site_ids() from 0006).

create table public.attributions (
    site_id bigint not null references public.sites (id) on delete cascade,
    month date not null check (extract(day from month) = 1),
    ai_patients int not null check (ai_patients between 0 and 10000),
    updated_at timestamptz not null default now(),
    primary key (site_id, month)
);

alter table public.attributions enable row level security;

revoke all on public.attributions from anon, authenticated;
grant select, insert, update on public.attributions to authenticated;

create policy attributions_read_own on public.attributions for select to authenticated
    using (site_id in (select private.my_site_ids()));

create policy attributions_insert_own on public.attributions for insert to authenticated
    with check (site_id in (select private.my_site_ids()));

create policy attributions_update_own on public.attributions for update to authenticated
    using (site_id in (select private.my_site_ids()))
    with check (site_id in (select private.my_site_ids()));
