-- Grissom Press attribution — initial schema.
-- Run in Supabase SQL editor after project creation.

create table if not exists public.events (
  id           bigserial primary key,
  brand        text not null,
  post_id      text,
  platform     text,
  event        text not null,
  utm_content  text,
  utm_campaign text,
  session_id   text not null,
  page_url     text,
  referrer     text,
  amount_cents integer,
  product_sku  text,
  ts           timestamptz not null default now(),
  ip_hash      text,
  ua_hash      text
);

create index if not exists events_brand_ts_idx  on public.events (brand, ts desc);
create index if not exists events_post_id_idx   on public.events (post_id) where post_id is not null;
create index if not exists events_event_ts_idx  on public.events (event, ts desc);

create materialized view if not exists public.weekly_post_performance as
select
  brand,
  post_id,
  platform,
  date_trunc('week', ts) as week,
  count(*) filter (where event = 'page_view')     as views,
  count(*) filter (where event = 'cta_click')     as clicks,
  count(*) filter (where event = 'email_capture') as captures,
  count(*) filter (where event = 'purchase')      as purchases,
  coalesce(sum(amount_cents) filter (where event = 'purchase'), 0) as revenue_cents,
  count(distinct session_id)                      as unique_sessions
from public.events
where post_id is not null
group by 1, 2, 3, 4;

create unique index if not exists wpp_pk on public.weekly_post_performance (brand, post_id, platform, week);

alter table public.events enable row level security;
-- No policies = only service-role key can read/write. That's the design.
