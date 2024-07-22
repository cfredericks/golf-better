create table pga_tournaments (
    id text primary key,
    name text not null,
    start_date date,
    is_completed boolean not null,
    data jsonb not null,
    last_updated timestamp with time zone not null
);
create index pga_tournaments_start_date on pga_tournaments (start_date);
create index pga_tournaments_is_completed on pga_tournaments (is_completed);

create table pga_players (
    id text primary key,
    name text not null,
    data jsonb not null,
    last_updated timestamp with time zone not null
);

create table pga_leaderboard_players (
    id text primary key,
    tournament_id text not null,
    player_id text not null references pga_players(id),
    data jsonb not null,
    last_updated timestamp with time zone not null
);
create index pga_leaderboard_players_tournament_id on pga_leaderboard_players (tournament_id);
create index pga_leaderboard_players_player_id on pga_leaderboard_players (player_id);

create table pga_player_scorecards (
    id text primary key,
    tournament_id text not null references pga_tournaments(id),
    player_id text not null references pga_players(id),
    data jsonb not null,
    last_updated timestamp with time zone not null
);
create index pga_player_scorecardss_tournament_id on pga_player_scorecards (tournament_id);
create index pga_player_scorecardss_player_id on pga_player_scorecards (player_id);

create table users (
    id text primary key,
    name text not null,
    email text not null unique,
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null,
    last_login timestamp with time zone not null
);

create table leagues (
    id text primary key,
    name text not null,
    owner_id text not null references users(id),
    start_date date not null,
    end_date date not null,
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null
);
create index leagues_owner_id on leagues (owner_id);
create index leagues_start_date on leagues (start_date);
create index leagues_end_date on leagues (end_date);

create table league_members (
    league_id text not null references leagues(id),
    user_id text not null references users(id),
    type text not null,
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null,
    primary key(league_id, user_id)
);
create index league_members_user_id on league_members (user_id);

create table player_groups (
    id text primary key,
    name text not null,
    owner_id text not null references users(id),
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null
);
create index player_groups_owner_id on player_groups (owner_id);

create table player_group_members (
    player_group_id text not null references player_groups(id),
    player_id text not null references pga_players(id),
    -- TODO allow changing group member status per round, for example
    status text not null, -- e.g. Active, Bench
    created timestamp with time zone not null,
    last_updated timestamp with time zone not null,
    primary key(player_group_id, player_id)
);
create index player_group_members_player_id on player_group_members (player_id);

-- TODO add other tables/fields to define the actual content and result/status of bets
create table bets (
    id text primary key,
    time_frame text not null -- e.g. Hole, Round, Tournament, Season, etc.
);

create table bet_instances (
    id text primary key,
    owner_id text not null references users(id),
    league_id text not null references leagues(id),
    bet_id text not null references bets(id),
    player_group_id text not null references player_groups(id)
    -- TODO add other tables/fields to define the actual content and result/status of bets
);
create index bet_instances_owner_id on bet_instances (owner_id);
create index bet_instances_league_id on bet_instances (league_id);
create index bet_instances_bet_id on bet_instances (bet_id);
create index bet_instances_player_group_id on bet_instances (player_group_id);
