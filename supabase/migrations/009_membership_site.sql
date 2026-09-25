-- 009_membership_site.sql — 趣学岛 FunLearn Island 会员内容站
-- profiles / memberships / content_items / RLS / storage

-- ---------- profiles ----------
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  created_at timestamptz not null default now()
);

-- ---------- memberships ----------
create table if not exists public.memberships (
  user_id uuid primary key references auth.users(id) on delete cascade,
  status text not null default 'inactive'
    check (status in ('inactive','trialing','active','past_due','canceled')),
  plan_id text check (plan_id in ('monthly','yearly')),
  stripe_customer_id text,
  stripe_subscription_id text unique,
  current_period_end timestamptz,
  cancel_at_period_end boolean not null default false,
  updated_at timestamptz not null default now()
);

-- ---------- content_items ----------
create table if not exists public.content_items (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  excerpt text not null default '',
  body_markdown text not null default '',
  tier text not null default 'free' check (tier in ('free','member')),
  kind text not null default 'article' check (kind in ('article','download')),
  file_path text, -- path inside member-files bucket (for kind='download')
  cover_emoji text not null default '📚',
  published boolean not null default false,
  sort_order int not null default 0,
  created_at timestamptz not null default now()
);

-- ---------- helper: active member? ----------
create or replace function public.is_active_member()
returns boolean
language sql
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.memberships m
    where m.user_id = auth.uid()
      and m.status in ('active','trialing')
      and (m.current_period_end is null or m.current_period_end > now())
  );
$$;

-- ---------- RLS ----------
alter table public.profiles enable row level security;
alter table public.memberships enable row level security;
alter table public.content_items enable row level security;

drop policy if exists "profiles_owner_read" on public.profiles;
create policy "profiles_owner_read" on public.profiles
  for select using (auth.uid() = id);
drop policy if exists "profiles_owner_insert" on public.profiles;
create policy "profiles_owner_insert" on public.profiles
  for insert with check (auth.uid() = id);
drop policy if exists "profiles_owner_update" on public.profiles;
create policy "profiles_owner_update" on public.profiles
  for update using (auth.uid() = id);

-- memberships: readable by owner; writes go through Edge Functions (service role)
drop policy if exists "memberships_owner_read" on public.memberships;
create policy "memberships_owner_read" on public.memberships
  for select using (auth.uid() = user_id);

-- content: free items public; member items require active membership
drop policy if exists "content_free_read" on public.content_items;
create policy "content_free_read" on public.content_items
  for select using (published and tier = 'free');
drop policy if exists "content_member_read" on public.content_items;
create policy "content_member_read" on public.content_items
  for select using (published and tier = 'member' and public.is_active_member());

-- ---------- auto-create profile on signup ----------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- storage: private bucket for member downloads ----------
insert into storage.buckets (id, name, public)
values ('member-files', 'member-files', false)
on conflict (id) do nothing;

drop policy if exists "member_files_read" on storage.objects;
create policy "member_files_read" on storage.objects
  for select using (
    bucket_id = 'member-files' and public.is_active_member()
  );
