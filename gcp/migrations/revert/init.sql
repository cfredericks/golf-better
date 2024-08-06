-- Revert golf-better:init from pg

begin;

drop table if exists golfbetter.pga_tournaments;
drop table if exists golfbetter.pga_players;
drop table if exists golfbetter.pga_leaderboard_players;
drop table if exists golfbetter.pga_player_scorecards;
drop table if exists golfbetter.users;
drop table if exists golfbetter.player_groups;

commit;
