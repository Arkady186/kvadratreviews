-- ============================================================
-- 1) «Поддержка сайта»: сообщения посетителей об ошибках.
-- 2) Опросник: одна заявка с одного устройства.
-- Выполните целиком: Supabase → SQL Editor → New query → вставьте → Run.
-- (schema.sql и leads.sql уже должны быть выполнены.) Можно запускать повторно.
-- ============================================================

-- ---------- 1. Сообщения об ошибках ----------
create table if not exists public.bug_reports (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  kind        text not null default 'bug' check (kind in ('bug','ui','idea','other')),
  message     text not null check (char_length(message) between 5 and 2000),
  contact     text check (contact is null or char_length(contact) <= 120),
  page        text check (page is null or char_length(page) <= 300),
  ua          text check (ua is null or char_length(ua) <= 300),
  viewport    text check (viewport is null or char_length(viewport) <= 30),
  err         text check (err is null or char_length(err) <= 500),
  device_id   text check (device_id is null or char_length(device_id) <= 64),
  status      text not null default 'new' check (status in ('new','fixed')),
  admin_note  text check (admin_note is null or char_length(admin_note) <= 2000)
);

alter table public.bug_reports enable row level security;

-- посетитель может только ОТПРАВИТЬ сообщение (читать список не может)
drop policy if exists "visitor can insert bug" on public.bug_reports;
create policy "visitor can insert bug" on public.bug_reports for insert to anon, authenticated
  with check (status = 'new' and admin_note is null);

-- администратор видит и меняет всё
drop policy if exists "admin all bugs" on public.bug_reports;
create policy "admin all bugs" on public.bug_reports for all to authenticated
  using (public.is_admin()) with check (public.is_admin());

revoke all on public.bug_reports from anon;
grant insert on public.bug_reports to anon;
grant select, insert, update, delete on public.bug_reports to authenticated;

-- защита от потока подделок: не больше 20 сообщений за 10 минут на весь сайт
create or replace function public.bug_flood_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.bug_reports where created_at > now() - interval '10 minutes') >= 20 then
    raise exception 'too many reports, try later' using errcode = 'P0001';
  end if;
  return new;
end $$;
drop trigger if exists bug_flood on public.bug_reports;
create trigger bug_flood before insert on public.bug_reports for each row execute function public.bug_flood_guard();

-- ---------- 2. Одна заявка с одного устройства ----------
alter table public.leads add column if not exists device_id text check (device_id is null or char_length(device_id) <= 64);
alter table public.leads add column if not exists fp        text check (fp is null or char_length(fp) <= 80);

-- второй раз с того же устройства база заявку не примет
create unique index if not exists leads_one_per_device on public.leads (device_id) where device_id is not null;

-- «я уже отправлял заявку?» — отвечает только по своему идентификатору устройства
create or replace function public.my_lead_status(dev text) returns text
language sql security definer set search_path = public stable as $$
  select case when exists (select 1 from public.leads where device_id = dev) then 'sent' else 'none' end;
$$;
grant execute on function public.my_lead_status(text) to anon, authenticated;
