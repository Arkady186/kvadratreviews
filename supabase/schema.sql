-- ============================================================
-- Хранилище отзывов «Квадрат». Выполните целиком в Supabase:
-- Project → SQL Editor → New query → вставьте → Run.
-- ============================================================

create table if not exists public.reviews (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  name        text not null check (char_length(name) between 2 and 60),
  topic       text check (topic is null or char_length(topic) <= 20),
  rating      int  not null check (rating between 1 and 5),
  body        text not null check (char_length(body) between 10 and 800),
  device_id   text not null unique check (device_id ~ '^[a-f0-9-]{20,64}$'),  -- 1 отзыв с 1 устройства
  fp          text check (fp is null or char_length(fp) <= 64),
  status      text not null default 'pending' check (status in ('pending','approved','hidden'))
);

-- кто администратор (добавьте свою почту в конце файла)
create table if not exists public.admins (email text primary key);
alter table public.admins enable row level security;   -- без политик: таблицу не видит никто, кроме функции ниже

create or replace function public.is_admin() returns boolean
language sql security definer set search_path = public stable as $$
  select exists (select 1 from public.admins where lower(email) = lower(coalesce(auth.jwt() ->> 'email', '')));
$$;

alter table public.reviews enable row level security;

-- посетитель может только ДОБАВИТЬ отзыв «на проверке»; читать таблицу напрямую он не может
drop policy if exists "visitor can insert" on public.reviews;
create policy "visitor can insert" on public.reviews for insert to anon, authenticated
  with check (status = 'pending');

-- администратор видит и меняет всё
drop policy if exists "admin all" on public.reviews;
create policy "admin all" on public.reviews for all to authenticated
  using (public.is_admin()) with check (public.is_admin());

-- публичный список: только опубликованные, без идентификатора устройства
create or replace view public.public_reviews as
  select id, created_at, name, topic, rating, body from public.reviews where status = 'approved';
grant select on public.public_reviews to anon, authenticated;

-- статус «моего» отзыва по идентификатору устройства
create or replace function public.my_review_status(dev text) returns text
language sql security definer set search_path = public stable as $$
  select coalesce((select status from public.reviews where device_id = dev limit 1), 'none');
$$;
grant execute on function public.my_review_status(text) to anon, authenticated;

-- защита от потока подделок: не больше 15 новых отзывов за 10 минут на весь сайт
create or replace function public.reviews_flood_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.reviews where created_at > now() - interval '10 minutes') >= 15 then
    raise exception 'too many reviews, try later' using errcode = 'P0001';
  end if;
  return new;
end $$;
drop trigger if exists reviews_flood on public.reviews;
create trigger reviews_flood before insert on public.reviews for each row execute function public.reviews_flood_guard();

revoke all on public.reviews from anon;
grant insert on public.reviews to anon;
grant select, update, delete on public.reviews to authenticated;
grant insert on public.reviews to authenticated;

-- ВАЖНО: впишите почту, под которой будете входить в admin.html (и создайте этого пользователя
-- в Authentication → Users → Add user → Create new user, поставьте галочку Auto Confirm)
-- insert into public.admins(email) values ('ваша@почта.ru');
