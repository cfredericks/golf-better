"""Database queries for fantasy league operations."""

import json
import uuid
import secrets
from datetime import datetime
from typing import List, Dict, Optional
import sqlalchemy
from db_queries import DB_SCHEMA


def generate_invite_code() -> str:
    """Generate a random 8-character invite code."""
    return secrets.token_urlsafe(6)[:8].upper()


def get_leagues_for_user(db_conn, user_id: str) -> List[Dict]:
    """Get all leagues a user is a member of, plus public leagues."""
    query = f"""
        SELECT l.id, l.name, l.owner_id, l.league_type, l.tournament_id,
               l.roster_config, l.scoring_config, l.pick_deadline_type,
               l.invite_code, l.is_public, l.created,
               u.name as owner_name,
               (SELECT COUNT(*) FROM {DB_SCHEMA}.league_members lm WHERE lm.league_id = l.id) as member_count
        FROM {DB_SCHEMA}.leagues l
        LEFT JOIN {DB_SCHEMA}.users u ON l.owner_id = u.id
        WHERE l.id IN (
            SELECT league_id FROM {DB_SCHEMA}.league_members WHERE user_id = :user_id
        ) OR l.is_public = true
        ORDER BY l.created DESC
    """
    result = db_conn.execute(sqlalchemy.text(query), {"user_id": user_id})
    leagues = []
    for row in result:
        leagues.append({
            "id": str(row.id),
            "name": row.name,
            "ownerId": row.owner_id,
            "ownerName": row.owner_name,
            "leagueType": row.league_type,
            "tournamentId": row.tournament_id,
            "rosterConfig": row.roster_config if isinstance(row.roster_config, dict) else json.loads(row.roster_config),
            "scoringConfig": row.scoring_config if isinstance(row.scoring_config, dict) else json.loads(row.scoring_config),
            "pickDeadlineType": row.pick_deadline_type,
            "inviteCode": row.invite_code,
            "isPublic": row.is_public,
            "created": row.created.isoformat() if row.created else None,
            "memberCount": row.member_count,
        })
    return leagues


def get_league_by_id(db_conn, league_id: str, user_id: str) -> Optional[Dict]:
    """Get a league by ID if user has access."""
    query = f"""
        SELECT l.id, l.name, l.owner_id, l.league_type, l.tournament_id,
               l.roster_config, l.scoring_config, l.pick_deadline_type,
               l.invite_code, l.is_public, l.created,
               u.name as owner_name,
               (SELECT COUNT(*) FROM {DB_SCHEMA}.league_members lm WHERE lm.league_id = l.id) as member_count
        FROM {DB_SCHEMA}.leagues l
        LEFT JOIN {DB_SCHEMA}.users u ON l.owner_id = u.id
        WHERE l.id = :league_id::uuid
        AND (l.is_public = true OR l.id IN (
            SELECT league_id FROM {DB_SCHEMA}.league_members WHERE user_id = :user_id
        ))
    """
    result = db_conn.execute(sqlalchemy.text(query), {"league_id": league_id, "user_id": user_id})
    row = result.fetchone()
    if not row:
        return None

    return {
        "id": str(row.id),
        "name": row.name,
        "ownerId": row.owner_id,
        "ownerName": row.owner_name,
        "leagueType": row.league_type,
        "tournamentId": row.tournament_id,
        "rosterConfig": row.roster_config if isinstance(row.roster_config, dict) else json.loads(row.roster_config),
        "scoringConfig": row.scoring_config if isinstance(row.scoring_config, dict) else json.loads(row.scoring_config),
        "pickDeadlineType": row.pick_deadline_type,
        "inviteCode": row.invite_code,
        "isPublic": row.is_public,
        "created": row.created.isoformat() if row.created else None,
        "memberCount": row.member_count,
    }


def create_league(
    db_conn,
    name: str,
    owner_id: str,
    league_type: str,
    roster_config: Dict,
    scoring_config: Dict,
    pick_deadline_type: str = "tournament_start",
    tournament_id: Optional[str] = None,
    is_public: bool = False
) -> Dict:
    """Create a new league and add owner as first member."""
    league_id = str(uuid.uuid4())
    invite_code = generate_invite_code()
    now = datetime.utcnow()

    # Insert league
    insert_league = f"""
        INSERT INTO {DB_SCHEMA}.leagues
        (id, name, owner_id, league_type, tournament_id, roster_config, scoring_config,
         pick_deadline_type, invite_code, is_public, created)
        VALUES (:id::uuid, :name, :owner_id, :league_type, :tournament_id,
                :roster_config::jsonb, :scoring_config::jsonb,
                :pick_deadline_type, :invite_code, :is_public, :created)
    """
    db_conn.execute(sqlalchemy.text(insert_league), {
        "id": league_id,
        "name": name,
        "owner_id": owner_id,
        "league_type": league_type,
        "tournament_id": tournament_id,
        "roster_config": json.dumps(roster_config),
        "scoring_config": json.dumps(scoring_config),
        "pick_deadline_type": pick_deadline_type,
        "invite_code": invite_code,
        "is_public": is_public,
        "created": now,
    })

    # Add owner as first member
    insert_member = f"""
        INSERT INTO {DB_SCHEMA}.league_members (league_id, user_id, role, joined_at)
        VALUES (:league_id::uuid, :user_id, 'owner', :joined_at)
    """
    db_conn.execute(sqlalchemy.text(insert_member), {
        "league_id": league_id,
        "user_id": owner_id,
        "joined_at": now,
    })

    db_conn.commit()

    return {
        "id": league_id,
        "name": name,
        "ownerId": owner_id,
        "leagueType": league_type,
        "tournamentId": tournament_id,
        "rosterConfig": roster_config,
        "scoringConfig": scoring_config,
        "pickDeadlineType": pick_deadline_type,
        "inviteCode": invite_code,
        "isPublic": is_public,
        "created": now.isoformat(),
        "memberCount": 1,
    }


def update_league(db_conn, league_id: str, owner_id: str, updates: Dict) -> bool:
    """Update league settings. Only owner can update."""
    # Verify ownership
    check_query = f"""
        SELECT id FROM {DB_SCHEMA}.leagues WHERE id = :league_id::uuid AND owner_id = :owner_id
    """
    result = db_conn.execute(sqlalchemy.text(check_query), {"league_id": league_id, "owner_id": owner_id})
    if not result.fetchone():
        return False

    # Build update query
    allowed_fields = ["name", "is_public", "pick_deadline_type"]
    set_clauses = []
    params = {"league_id": league_id}

    for field in allowed_fields:
        if field in updates:
            set_clauses.append(f"{field} = :{field}")
            params[field] = updates[field]

    if not set_clauses:
        return True

    update_query = f"""
        UPDATE {DB_SCHEMA}.leagues SET {", ".join(set_clauses)} WHERE id = :league_id::uuid
    """
    db_conn.execute(sqlalchemy.text(update_query), params)
    db_conn.commit()
    return True


def get_league_members(db_conn, league_id: str) -> List[Dict]:
    """Get all members of a league."""
    query = f"""
        SELECT lm.id, lm.league_id, lm.user_id, lm.role, lm.joined_at, u.name as user_name
        FROM {DB_SCHEMA}.league_members lm
        JOIN {DB_SCHEMA}.users u ON lm.user_id = u.id
        WHERE lm.league_id = :league_id::uuid
        ORDER BY lm.joined_at
    """
    result = db_conn.execute(sqlalchemy.text(query), {"league_id": league_id})
    return [{
        "id": str(row.id),
        "leagueId": str(row.league_id),
        "userId": row.user_id,
        "userName": row.user_name,
        "role": row.role,
        "joinedAt": row.joined_at.isoformat() if row.joined_at else None,
    } for row in result]


def join_league(db_conn, league_id: str, user_id: str, invite_code: str) -> Optional[Dict]:
    """Join a league using invite code."""
    # Check invite code matches
    check_query = f"""
        SELECT id FROM {DB_SCHEMA}.leagues
        WHERE id = :league_id::uuid AND (invite_code = :invite_code OR is_public = true)
    """
    result = db_conn.execute(sqlalchemy.text(check_query), {"league_id": league_id, "invite_code": invite_code})
    if not result.fetchone():
        return None

    # Check not already a member
    member_check = f"""
        SELECT id FROM {DB_SCHEMA}.league_members WHERE league_id = :league_id::uuid AND user_id = :user_id
    """
    result = db_conn.execute(sqlalchemy.text(member_check), {"league_id": league_id, "user_id": user_id})
    if result.fetchone():
        return None  # Already a member

    # Add member
    now = datetime.utcnow()
    insert_member = f"""
        INSERT INTO {DB_SCHEMA}.league_members (league_id, user_id, role, joined_at)
        VALUES (:league_id::uuid, :user_id, 'member', :joined_at)
        RETURNING id
    """
    result = db_conn.execute(sqlalchemy.text(insert_member), {
        "league_id": league_id,
        "user_id": user_id,
        "joined_at": now,
    })
    member_id = str(result.fetchone().id)
    db_conn.commit()

    return {
        "id": member_id,
        "leagueId": league_id,
        "userId": user_id,
        "role": "member",
        "joinedAt": now.isoformat(),
    }


def create_invitation(db_conn, league_id: str, email: str, invited_by: str) -> Dict:
    """Create a league invitation."""
    now = datetime.utcnow()
    invitation_id = str(uuid.uuid4())

    insert_query = f"""
        INSERT INTO {DB_SCHEMA}.league_invitations (id, league_id, invited_email, invited_by, created)
        VALUES (:id::uuid, :league_id::uuid, :email, :invited_by, :created)
        ON CONFLICT (league_id, invited_email) DO UPDATE SET
            invited_by = EXCLUDED.invited_by,
            status = 'pending',
            created = EXCLUDED.created,
            expires_at = now() + interval '7 days'
        RETURNING id, expires_at
    """
    result = db_conn.execute(sqlalchemy.text(insert_query), {
        "id": invitation_id,
        "league_id": league_id,
        "email": email,
        "invited_by": invited_by,
        "created": now,
    })
    row = result.fetchone()
    db_conn.commit()

    return {
        "id": str(row.id),
        "leagueId": league_id,
        "invitedEmail": email,
        "invitedBy": invited_by,
        "status": "pending",
        "expiresAt": row.expires_at.isoformat() if row.expires_at else None,
    }


def get_user_picks(db_conn, league_id: str, user_id: str, tournament_id: Optional[str] = None) -> List[Dict]:
    """Get user's picks for a league, optionally filtered by tournament."""
    query = f"""
        SELECT tp.id, tp.league_id, tp.user_id, tp.tournament_id, tp.player_id,
               tp.tier, tp.salary, tp.picked_at, p.name as player_name
        FROM {DB_SCHEMA}.tournament_picks tp
        LEFT JOIN {DB_SCHEMA}.pga_players p ON tp.player_id = p.id
        WHERE tp.league_id = :league_id::uuid AND tp.user_id = :user_id
    """
    params = {"league_id": league_id, "user_id": user_id}

    if tournament_id:
        query += " AND tp.tournament_id = :tournament_id"
        params["tournament_id"] = tournament_id

    query += " ORDER BY tp.picked_at"

    result = db_conn.execute(sqlalchemy.text(query), params)
    return [{
        "id": str(row.id),
        "leagueId": str(row.league_id),
        "userId": row.user_id,
        "tournamentId": row.tournament_id,
        "playerId": row.player_id,
        "playerName": row.player_name,
        "tier": row.tier,
        "salary": row.salary,
        "pickedAt": row.picked_at.isoformat() if row.picked_at else None,
    } for row in result]


def submit_picks(
    db_conn,
    league_id: str,
    user_id: str,
    tournament_id: str,
    player_ids: List[str]
) -> List[Dict]:
    """Submit or update picks for a tournament."""
    now = datetime.utcnow()

    # Delete existing picks for this tournament
    delete_query = f"""
        DELETE FROM {DB_SCHEMA}.tournament_picks
        WHERE league_id = :league_id::uuid AND user_id = :user_id AND tournament_id = :tournament_id
    """
    db_conn.execute(sqlalchemy.text(delete_query), {
        "league_id": league_id,
        "user_id": user_id,
        "tournament_id": tournament_id,
    })

    # Insert new picks
    picks = []
    for player_id in player_ids:
        pick_id = str(uuid.uuid4())
        insert_query = f"""
            INSERT INTO {DB_SCHEMA}.tournament_picks (id, league_id, user_id, tournament_id, player_id, picked_at)
            VALUES (:id::uuid, :league_id::uuid, :user_id, :tournament_id, :player_id, :picked_at)
        """
        db_conn.execute(sqlalchemy.text(insert_query), {
            "id": pick_id,
            "league_id": league_id,
            "user_id": user_id,
            "tournament_id": tournament_id,
            "player_id": player_id,
            "picked_at": now,
        })
        picks.append({
            "id": pick_id,
            "leagueId": league_id,
            "userId": user_id,
            "tournamentId": tournament_id,
            "playerId": player_id,
            "pickedAt": now.isoformat(),
        })

    db_conn.commit()
    return picks


def get_available_players(db_conn, tournament_id: str) -> List[Dict]:
    """Get players available for picking in a tournament."""
    query = f"""
        SELECT lp.player_id, p.name, p.data
        FROM {DB_SCHEMA}.pga_leaderboard_players lp
        LEFT JOIN {DB_SCHEMA}.pga_players p ON lp.player_id = p.id
        WHERE lp.tournament_id = :tournament_id
        ORDER BY p.name
    """
    result = db_conn.execute(sqlalchemy.text(query), {"tournament_id": tournament_id})

    players = []
    tier = 1
    for i, row in enumerate(result):
        # Simple tier assignment based on position in list
        if i >= 30:
            tier = 4
        elif i >= 15:
            tier = 3
        elif i >= 5:
            tier = 2

        player_data = row.data if isinstance(row.data, dict) else json.loads(row.data) if row.data else {}
        players.append({
            "id": row.player_id,
            "name": row.name or player_data.get("name", "Unknown"),
            "tier": tier,
            "salary": 10000 - (i * 100),  # Simple salary calculation
            "worldRanking": player_data.get("worldRanking"),
        })

    return players


def get_league_standings(db_conn, league_id: str) -> List[Dict]:
    """Get overall standings for a league."""
    query = f"""
        SELECT fs.user_id, u.name as user_name, SUM(fs.total_score) as total_score
        FROM {DB_SCHEMA}.fantasy_scores fs
        JOIN {DB_SCHEMA}.users u ON fs.user_id = u.id
        WHERE fs.league_id = :league_id::uuid
        GROUP BY fs.user_id, u.name
        ORDER BY total_score DESC
    """
    result = db_conn.execute(sqlalchemy.text(query), {"league_id": league_id})

    standings = []
    for rank, row in enumerate(result, 1):
        standings.append({
            "userId": row.user_id,
            "userName": row.user_name,
            "totalScore": float(row.total_score) if row.total_score else 0,
            "rank": rank,
        })

    return standings


def get_tournament_scoring(db_conn, league_id: str, tournament_id: str) -> List[Dict]:
    """Get detailed scoring for a tournament in a league."""
    query = f"""
        SELECT fs.id, fs.user_id, fs.tournament_id, fs.player_scores,
               fs.total_score, fs.rank, fs.calculated_at, u.name as user_name
        FROM {DB_SCHEMA}.fantasy_scores fs
        JOIN {DB_SCHEMA}.users u ON fs.user_id = u.id
        WHERE fs.league_id = :league_id::uuid AND fs.tournament_id = :tournament_id
        ORDER BY fs.rank
    """
    result = db_conn.execute(sqlalchemy.text(query), {
        "league_id": league_id,
        "tournament_id": tournament_id,
    })

    scores = []
    for row in result:
        player_scores = row.player_scores if isinstance(row.player_scores, list) else json.loads(row.player_scores)
        scores.append({
            "id": str(row.id),
            "userId": row.user_id,
            "userName": row.user_name,
            "tournamentId": row.tournament_id,
            "playerScores": player_scores,
            "totalScore": float(row.total_score) if row.total_score else 0,
            "rank": row.rank,
            "calculatedAt": row.calculated_at.isoformat() if row.calculated_at else None,
        })

    return scores


def get_user_favorites(db_conn, user_id: str) -> List[Dict]:
    """Get user's favorites."""
    query = f"""
        SELECT id, favorite_type, target_id, created
        FROM {DB_SCHEMA}.user_favorites
        WHERE user_id = :user_id
        ORDER BY created DESC
    """
    result = db_conn.execute(sqlalchemy.text(query), {"user_id": user_id})
    return [{
        "id": str(row.id),
        "userId": user_id,
        "favoriteType": row.favorite_type,
        "targetId": row.target_id,
    } for row in result]


def add_favorite(db_conn, user_id: str, favorite_type: str, target_id: str) -> Dict:
    """Add a favorite."""
    now = datetime.utcnow()
    fav_id = str(uuid.uuid4())

    insert_query = f"""
        INSERT INTO {DB_SCHEMA}.user_favorites (id, user_id, favorite_type, target_id, created)
        VALUES (:id::uuid, :user_id, :favorite_type, :target_id, :created)
        ON CONFLICT (user_id, favorite_type, target_id) DO NOTHING
        RETURNING id
    """
    result = db_conn.execute(sqlalchemy.text(insert_query), {
        "id": fav_id,
        "user_id": user_id,
        "favorite_type": favorite_type,
        "target_id": target_id,
        "created": now,
    })
    row = result.fetchone()
    db_conn.commit()

    return {
        "id": str(row.id) if row else fav_id,
        "userId": user_id,
        "favoriteType": favorite_type,
        "targetId": target_id,
    }


def delete_favorite(db_conn, favorite_id: str, user_id: str) -> bool:
    """Delete a favorite."""
    delete_query = f"""
        DELETE FROM {DB_SCHEMA}.user_favorites WHERE id = :id::uuid AND user_id = :user_id
    """
    result = db_conn.execute(sqlalchemy.text(delete_query), {"id": favorite_id, "user_id": user_id})
    db_conn.commit()
    return result.rowcount > 0
