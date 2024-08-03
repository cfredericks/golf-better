-- Verify golf-better:init on pg

begin;

set schema 'golfbetter';

select id, name, start_date, is_completed, data, last_updated
from pga_tournaments
where false;

select id, name, data, last_updated
from pga_players
where false;

select id, tournament_id, player_id, data, last_updated
from pga_leaderboard_players
where false;

select id, tournament_id, player_id, data, last_updated
from pga_player_scorecards
where false;

select id, name, email, created, last_updated, last_login
from users
where false;

select id, name, owner_id, player_id, created, last_updated
from player_groups
where false;

rollback;
