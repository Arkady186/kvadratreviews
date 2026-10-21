-- ============================================================
-- Заявки из опросника «Дизайн-проект мебели» + загрузка файлов.
-- Выполните целиком: Supabase → SQL Editor → New query → вставьте → Run.
-- (schema.sql с отзывами уже должен быть выполнен — оттуда берётся is_admin().)
-- Скрипт можно запускать повторно.
-- ============================================================

create table if not exists public.leads (
  id          uuid primary key,
  created_at  timestamptz not null default now(),
  items       text[]  not null check (cardinality(items) between 1 and 12),
  items_other text    check (items_other is null or char_length(items_other) <= 200),
  stage       text    not null check (char_length(stage) between 1 and 80),
  plan        text    not null check (char_length(plan) between 1 and 80),
  name        text    not null check (char_length(name) between 2 and 80),
  phone       text    not null check (char_length(phone) between 10 and 24),
  comment     text    check (comment is null or char_length(comment) <= 2000),
  files       jsonb   not null default '[]'::jsonb check (jsonb_typeof(files) = 'array' and jsonb_array_length(files) <= 10),
  status      text    not null default 'new' check (status in ('new','work','done')),
  admin_note  text    check (admin_note is null or char_length(admin_note) <= 2000)
);

alter table public.leads enable row level security;

-- посетитель может только ДОБАВИТЬ заявку (читать список он не может)
drop policy if exists "visitor can insert lead" on public.leads;
create policy "visitor can insert lead" on public.leads for insert to anon, authenticated
  with check (status = 'new' and admin_note is null);

-- администратор видит и меняет всё
drop policy if exists "admin all leads" on public.leads;
create policy "admin all leads" on public.leads for all to authenticated
  using (public.is_admin()) with check (public.is_admin());

revoke all on public.leads from anon;
grant insert on public.leads to anon;
grant select, insert, update, delete on public.leads to authenticated;

-- защита от потока подделок: не больше 30 заявок за 10 минут на весь сайт
create or replace function public.leads_flood_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.leads where created_at > now() - interval '10 minutes') >= 30 then
    raise exception 'too many leads, try later' using errcode = 'P0001';
  end if;
  return new;
end $$;
drop trigger if exists leads_flood on public.leads;
create trigger leads_flood before insert on public.leads for each row execute function public.leads_flood_guard();

-- ---------- Файлы (план, чертёж, фото, референсы) ----------
-- Закрытое хранилище: до 10 МБ на файл, только картинки и PDF.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('lead-files', 'lead-files', false, 10485760,
        array['image/jpeg','image/png','image/webp','image/heic','image/heif','application/pdf'])
on conflict (id) do update set public = false, file_size_limit = 10485760,
  allowed_mime_types = array['image/jpeg','image/png','image/webp','image/heic','image/heif','application/pdf'];

-- загружать может любой посетитель, но только в папку вида <uuid>/<номер>-<имя>
drop policy if exists "visitor can upload lead files" on storage.objects;
create policy "visitor can upload lead files" on storage.objects for insert to anon, authenticated
  with check (bucket_id = 'lead-files' and name ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[0-9]{1,2}-[A-Za-z0-9._-]{1,80}$');

-- смотреть и удалять файлы может только администратор
drop policy if exists "admin reads lead files" on storage.objects;
create policy "admin reads lead files" on storage.objects for select to authenticated
  using (bucket_id = 'lead-files' and public.is_admin());
drop policy if exists "admin deletes lead files" on storage.objects;
create policy "admin deletes lead files" on storage.objects for delete to authenticated
  using (bucket_id = 'lead-files' and public.is_admin());
