-- Deploy golf-better:fantasy_leagues to pg

begin;

set schema 'golfbetter';

-- Leagues table
create table if not exists leagues (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    owner_id text not null references users(id),
    league_type text not null check (league_type in ('season', 'tournament')),
    tournament_id text references pga_tournaments(id),
    roster_config jsonb not null,
    scoring_config jsonb not null,
    pick_deadline_type text not null default 'tournament_start',
    invite_code text unique,
    is_public boolean default false,
    created timestamp with time zone default now()
);
create index if not exists leagues_owner_id on leagues (owner_id);
create index if not exists leagues_is_public on leagues (is_public);

-- League members table
create table if not exists league_members (
    id uuid primary key default gen_random_uuid(),
    league_id uuid references leagues(id) on delete cascade,
    user_id text references users(id),
    role text default 'member' check (role in ('owner', 'admin', 'member')),
    joined_at timestamp with time zone default now(),
    unique(league_id, user_id)
);
create index if not exists league_members_league_id on league_members (league_id);
create index if not exists league_members_user_id on league_members (user_id);

-- Tournament picks table
create table if not exists tournament_picks (
    id uuid primary key default gen_random_uuid(),
    league_id uuid references leagues(id) on delete cascade,
    user_id text references users(id),
    tournament_id text references pga_tournaments(id),
    player_id text not null,
    tier integer,
    salary integer,
    picked_at timestamp with time zone default now(),
    unique(league_id, user_id, tournament_id, player_id)
);
create index if not exists tournament_picks_league_id on tournament_picks (league_id);
create index if not exists tournament_picks_user_id on tournament_picks (user_id);
create index if not exists tournament_picks_tournament_id on tournament_picks (tournament_id);

-- Fantasy scores table (cached, computed by background job)
create table if not exists fantasy_scores (
    id uuid primary key default gen_random_uuid(),
    league_id uuid references leagues(id) on delete cascade,
    user_id text references users(id),
    tournament_id text references pga_tournaments(id),
    player_scores jsonb not null,
    total_score decimal(10,2) default 0,
    rank integer,
    calculated_at timestamp with time zone default now(),
    unique(league_id, user_id, tournament_id)
);
create index if not exists fantasy_scores_league_id on fantasy_scores (league_id);
create index if not exists fantasy_scores_tournament_id on fantasy_scores (tournament_id);

-- User favorites table
create table if not exists user_favorites (
    id uuid primary key default gen_random_uuid(),
    user_id text references users(id),
    favorite_type text check (favorite_type in ('player', 'tournament')),
    target_id text not null,
    created timestamp with time zone default now(),
    unique(user_id, favorite_type, target_id)
);
create index if not exists user_favorites_user_id on user_favorites (user_id);

-- League invitations table
create table if not exists league_invitations (
    id uuid primary key default gen_random_uuid(),
    league_id uuid references leagues(id) on delete cascade,
    invited_email text not null,
    invited_by text references users(id),
    status text default 'pending' check (status in ('pending', 'accepted', 'declined', 'expired')),
    expires_at timestamp with time zone default (now() + interval '7 days'),
    created timestamp with time zone default now(),
    unique(league_id, invited_email)
);
create index if not exists league_invitations_league_id on league_invitations (league_id);
create index if not exists league_invitations_invited_email on league_invitations (invited_email);
create index if not exists league_invitations_status on league_invitations (status);

commit;
