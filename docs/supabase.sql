-- Learnino: Online-Speicher für den Lernstand (in Supabase unter "SQL Editor" einfügen und "Run" drücken)
create table if not exists public.learnino_state (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.learnino_state enable row level security;

-- Jede angemeldete Familie sieht und ändert nur ihre eigene Zeile
create policy "eigene Daten lesen" on public.learnino_state
  for select to authenticated using (auth.uid() = user_id);
create policy "eigene Daten anlegen" on public.learnino_state
  for insert to authenticated with check (auth.uid() = user_id);
create policy "eigene Daten ändern" on public.learnino_state
  for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
