-- Revert golf-better:fantasy_leagues from pg

begin;

set schema 'golfbetter';

drop table if exists league_invitations;
drop table if exists user_favorites;
drop table if exists fantasy_scores;
drop table if exists tournament_picks;
drop table if exists league_members;
drop table if exists leagues;

commit;
