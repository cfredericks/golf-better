-- Verify golf-better:fantasy_leagues on pg

begin;

set schema 'golfbetter';

select id, name, owner_id, league_type, tournament_id, roster_config, scoring_config,
       pick_deadline_type, invite_code, is_public, created
from leagues where false;

select id, league_id, user_id, role, joined_at
from league_members where false;

select id, league_id, user_id, tournament_id, player_id, tier, salary, picked_at
from tournament_picks where false;

select id, league_id, user_id, tournament_id, player_scores, total_score, rank, calculated_at
from fantasy_scores where false;

select id, user_id, favorite_type, target_id, created
from user_favorites where false;

select id, league_id, invited_email, invited_by, status, expires_at, created
from league_invitations where false;

rollback;
