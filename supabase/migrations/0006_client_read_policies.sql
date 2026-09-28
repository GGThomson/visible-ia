-- 0006_client_read_policies.sql · each client sees only its own data (C7-T02, PRD §6, HU-19)
--
-- Panel users are Supabase Auth users linked to one client (public.app_users). Everything
-- they can see is derived from auth.uid() by the private.my_* functions below:
--   - their client (and, for an agency, the clinics it manages),
--   - their active sites, the clinics of those sites and the markets they are in.
-- They read the market-level measurements of their markets (the ranking shows competitors
-- by name and index) and only their own reports, tasks, sites and client row. Raw answer
-- text (public.responses) is never exposed. anon keeps no access at all (except the landing
-- insert of 0005). Writes stay with the service role, except marking their own tasks done.

create schema if not exists private;
revoke all on schema private from public, anon;
grant usage on schema private to authenticated;

-- security definer: they read app_users/sites/clients regardless of RLS, only for auth.uid().
create or replace function private.my_client_ids() returns setof bigint
language sql stable security definer set search_path = '' as $$
    select u.client_id from public.app_users u where u.id = auth.uid()
    union
    select c.id from public.clients c
    join public.app_users u on u.client_id = c.parent_agency_id
    where u.id = auth.uid() and u.role = 'agency'
$$;

create or replace function private.my_site_ids() returns setof bigint
language sql stable security definer set search_path = '' as $$
    select s.id from public.sites s
    where s.client_id in (select private.my_client_ids())
      and (s.active_to is null or s.active_to >= current_date)
$$;

create or replace function private.my_clinic_ids() returns setof bigint
language sql stable security definer set search_path = '' as $$
    select s.clinic_id from public.sites s where s.id in (select private.my_site_ids())
$$;

create or replace function private.my_market_ids() returns setof bigint
language sql stable security definer set search_path = '' as $$
    select s.market_id from public.sites s where s.id in (select private.my_site_ids())
$$;

-- Clinics of their markets (the competitors in the ranking). clinic_markets itself stays
-- closed to authenticated, so this must be a definer function too.
create or replace function private.my_market_clinic_ids() returns setof bigint
language sql stable security definer set search_path = '' as $$
    select cm.clinic_id from public.clinic_markets cm
    where cm.market_id in (select private.my_market_ids())
$$;

revoke all on function private.my_client_ids(), private.my_site_ids(),
    private.my_clinic_ids(), private.my_market_ids(), private.my_market_clinic_ids()
    from public, anon;
grant execute on function private.my_client_ids(), private.my_site_ids(),
    private.my_clinic_ids(), private.my_market_ids(), private.my_market_clinic_ids()
    to authenticated;

-- Own rows --------------------------------------------------------------------------------
create policy clients_read_own on public.clients for select to authenticated
    using (id in (select private.my_client_ids()));

create policy app_users_read_self on public.app_users for select to authenticated
    using (id = auth.uid());

create policy sites_read_own on public.sites for select to authenticated
    using (id in (select private.my_site_ids()));

create policy reports_read_own on public.reports for select to authenticated
    using (clinic_id in (select private.my_clinic_ids())
           or site_id in (select private.my_site_ids()));

create policy tasks_read_own on public.tasks for select to authenticated
    using (site_id in (select private.my_site_ids()));

-- HU-20: a clinic marks its own checklist tasks as done (only status and updated_at).
revoke update on public.tasks from authenticated;
grant update (status, updated_at) on public.tasks to authenticated;
create policy tasks_update_own on public.tasks for update to authenticated
    using (site_id in (select private.my_site_ids()))
    with check (site_id in (select private.my_site_ids()));

-- Market-level data of their markets ------------------------------------------------------
create policy monthly_scores_read_my_markets on public.monthly_scores for select to authenticated
    using (market_id in (select private.my_market_ids()));

create policy markets_read_mine on public.markets for select to authenticated
    using (id in (select private.my_market_ids()));

create policy clinics_read_my_markets on public.clinics for select to authenticated
    using (id in (select private.my_market_clinic_ids()));

create policy mentions_read_my_markets on public.mentions for select to authenticated
    using (response_id in (select r.id from public.responses r
                           join public.runs ru on ru.id = r.run_id
                           where ru.market_id in (select private.my_market_ids())
                             and ru.kind = 'api' and ru.status = 'reviewed'));

create policy sources_read_my_markets on public.sources for select to authenticated
    using (response_id in (select r.id from public.responses r
                           join public.runs ru on ru.id = r.run_id
                           where ru.market_id in (select private.my_market_ids())
                             and ru.kind = 'api' and ru.status = 'reviewed'));

-- Panel views (read only). security_invoker: the policies above apply to whoever reads.
create or replace view public.v_panel_ranking with (security_invoker = true) as
select
    s.market_id,
    s.month,
    s.clinic_id,
    c.name as clinic_name,
    (s.clinic_id in (select private.my_clinic_ids())) as is_mine,
    s.presence_index as combined,
    s.ci_low,
    s.ci_high,
    s.change,
    s.window3_index,
    s.detectable_diff,
    s.avg_position,
    s.mention_share,
    -- A surface with no answers that month is shown as empty, not as 0 %.
    (case when g.n_responses > 0 then g.presence_index end)::numeric(5, 2) as chatgpt,
    (case when o.n_responses > 0 then o.presence_index end)::numeric(5, 2) as google
from public.monthly_scores s
join public.clinics c on c.id = s.clinic_id
left join public.monthly_scores g on g.market_id = s.market_id and g.month = s.month
    and g.clinic_id = s.clinic_id and g.surface = 'chatgpt_api'
left join public.monthly_scores o on o.market_id = s.market_id and o.month = s.month
    and o.clinic_id = s.clinic_id and o.surface = 'google_ai_mode'
where s.surface = 'combined';

create or replace view public.v_panel_evolution with (security_invoker = true) as
select s.id as site_id, m.market_id, m.month, m.surface, m.presence_index, m.ci_low,
       m.ci_high, m.change, m.window3_index, m.window3_ci_low, m.window3_ci_high,
       m.n_responses, m.appearances
from public.sites s
join public.monthly_scores m on m.market_id = s.market_id and m.clinic_id = s.clinic_id;

-- Sources aggregated per market and month: domain, type and how many answers cite it.
create or replace view public.v_panel_sources with (security_invoker = true) as
select ru.market_id, ru.month, src.domain, src.source_type,
       count(distinct src.response_id) as answers
from public.sources src
join public.responses r on r.id = src.response_id
join public.runs ru on ru.id = r.run_id
where ru.kind = 'api' and ru.status = 'reviewed'
group by ru.market_id, ru.month, src.domain, src.source_type;

revoke all on public.v_panel_ranking, public.v_panel_evolution, public.v_panel_sources
    from anon, public;
grant select on public.v_panel_ranking, public.v_panel_evolution, public.v_panel_sources
    to authenticated;

-- v_panel_sources joins responses/runs: authenticated needs to read the rows behind it, but
-- only through the view's columns. Row access is limited to reviewed API runs of its markets.
create policy runs_read_my_markets on public.runs for select to authenticated
    using (market_id in (select private.my_market_ids()) and kind = 'api' and status = 'reviewed');
create policy responses_read_ids_my_markets on public.responses for select to authenticated
    using (run_id in (select ru.id from public.runs ru
                      where ru.market_id in (select private.my_market_ids())
                        and ru.kind = 'api' and ru.status = 'reviewed'));
-- ...but never the raw text or payload of the answers.
revoke select on public.responses from authenticated;
grant select (id, run_id, question_id, surface, repetition, created_at)
    on public.responses to authenticated;
