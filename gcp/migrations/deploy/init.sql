-- Deploy golf-better:init to pg

begin;

set schema 'golfbetter';

create table if not exists pga_tournaments (
    id text primary key,
    name text not null,
    start_date date,
    is_completed boolean not null,
    data jsonb not null,
    last_updated timestamp with time zone not null
);
create index if not exists pga_tournaments_start_date on pga_tournaments (start_date);
create index if not exists pga_tournaments_is_completed on pga_tournaments (is_completed);

create table if not exists pga_players (
    id text primary key,
    name text not null,
    data jsonb not null,
    last_updated timestamp with time zone not null
);

create table if not exists pga_leaderboard_players (
    id text primary key,
    tournament_id text not null,
    player_id text not null,
    data jsonb not null,
    last_updated timestamp with time zone not null
);
create index if not exists pga_leaderboard_players_tournament_id on pga_leaderboard_players (tournament_id);
create index if not exists pga_leaderboard_players_player_id on pga_leaderboard_players (player_id);

create table if not exists pga_player_scorecards (
    id text primary key,
    tournament_id text not null,
    player_id text not null,
    data jsonb not null,
    last_updated timestamp with time zone not null
);
create index if not exists pga_player_scorecardss_tournament_id on pga_player_scorecards (tournament_id);
create index if not exists pga_player_scorecardss_player_id on pga_player_scorecards (player_id);

create table if not exists users (
    id text primary key,
    name text not null,
    email text not null unique,
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null,
    last_login timestamp with time zone not null
);

create table if not exists player_groups (
    id text primary key,
    name text not null,
    owner_id text not null references users(id),
    player_id text not null,
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null
);
create index if not exists player_groups_owner_id on player_groups (owner_id);
create index if not exists player_groups_player_id on player_groups (player_id);

commit;
