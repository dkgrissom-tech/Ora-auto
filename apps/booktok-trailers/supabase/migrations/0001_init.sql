-- BookTok Trailer Factory — schema v1

create extension if not exists "pgcrypto";

-- users: mirrors auth.users, holds plan state
create table if not exists public.users (
  id uuid primary key references auth.users on delete cascade,
  email text,
  stripe_customer_id text,
  stripe_subscription_id text,
  plan text not null default 'trial',
  quota_per_week int not null default 1,
  subscription_status text not null default 'trialing',
  created_at timestamptz not null default now()
);

-- orders: one per Amazon URL submission
create table if not exists public.orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  amazon_url text not null,
  title text,
  author text,
  status text not null default 'queued',
  error text,
  created_at timestamptz not null default now()
);

create index if not exists orders_user_created_idx on public.orders(user_id, created_at desc);

-- generations: one row per preset per order
create table if not exists public.generations (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders(id) on delete cascade,
  preset_id text not null,
  video_url text,
  created_at timestamptz not null default now()
);

create index if not exists generations_order_idx on public.generations(order_id);

-- RLS
alter table public.users enable row level security;
alter table public.orders enable row level security;
alter table public.generations enable row level security;

create policy "users_self_read" on public.users for select using (auth.uid() = id);
create policy "orders_self_all" on public.orders for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "generations_self_read" on public.generations for select using (
  exists (select 1 from public.orders o where o.id = order_id and o.user_id = auth.uid())
);

-- Weekly usage RPC (rolling 7-day count of completed or in-flight orders)
create or replace function public.weekly_usage(p_user_id uuid)
returns int language sql stable as $$
  select count(*)::int
  from public.orders
  where user_id = p_user_id
    and created_at > now() - interval '7 days'
    and status <> 'failed';
$$;

-- Auto-provision a users row on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.users (id, email) values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();
