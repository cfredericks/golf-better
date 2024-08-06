"""
Helpers for querying the database and converting to application data models.
"""

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

import sqlalchemy
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .models import PGATournament, PGAPlayer, PGALeaderboardPlayer, PGAPlayerScorecard, User
from .schemas import PGATournamentSchema, PGAPlayerSchema, PGALeaderboardPlayerSchema, PGAPlayerScorecardSchema, UserSchema
from datetime import datetime

def get_tournaments(session: Session, id: str):
    query = session.query(PGATournament)

    filters = []
    if id:
        filters.append(PGATournament.id == id)

    if filters:
        query = query.filter(and_(*filters))

    records = query.all()
    schema = PGATournamentSchema(many=True)
    # TODO - this is not very performant, find a better way to serialize to data models in one step
    return schema.load(schema.dump(records))

def get_players(session: Session, id: str):
    query = session.query(PGAPlayer)

    filters = []
    if id:
        filters.append(PGAPlayer.id == id)

    if filters:
        query = query.filter(and_(*filters))

    records = query.all()
    schema = PGAPlayerSchema(many=True)
    # TODO - this is not very performant, find a better way to serialize to data models in one step
    return schema.load(schema.dump(records))

def get_leaderboard_players(session: Session, id: str, player_id: str, tournament_id: str):
    query = session.query(PGALeaderboardPlayer)

    filters = []
    if id:
        filters.append(PGALeaderboardPlayer.id == id)
    if player_id:
        filters.append(PGALeaderboardPlayer.player_id == player_id)
    if tournament_id:
        filters.append(PGALeaderboardPlayer.tournament_id == tournament_id)

    if filters:
        query = query.filter(and_(*filters))

    records = query.all()
    schema = PGALeaderboardPlayerSchema(many=True)
    # TODO - this is not very performant, find a better way to serialize to data models in one step
    return schema.load(schema.dump(records))

def get_player_scorecards(session: Session, id: str, player_id: str, tournament_id: str):
    query = session.query(PGAPlayerScorecard)

    filters = []
    if id:
        filters.append(PGAPlayerScorecard.id == id)
    if player_id:
        filters.append(PGAPlayerScorecard.player_id == player_id)
    if tournament_id:
        filters.append(PGAPlayerScorecard.tournament_id == tournament_id)

    if filters:
        query = query.filter(and_(*filters))

    records = query.all()
    schema = PGAPlayerScorecardSchema(many=True)
    # TODO - this is not very performant, find a better way to serialize to data models in one step
    return schema.load(schema.dump(records))

def get_users(session: Session, id: str, email: str):
    query = session.query(User)

    filters = []
    if id:
        filters.append(User.id == id)
    if email:
        filters.append(User.email == email)

    if filters:
        query = query.filter(and_(*filters))

    records = query.all()
    schema = UserSchema(many=True)
    # TODO - this is not very performant, find a better way to serialize to data models in one step
    return schema.load(schema.dump(records))

def upsert_user(db: Session, id: str, name: str, email: str):
    now = datetime.utcnow()

    stmt = insert(User).values(
        id=id or email,
        name=name or email,
        email=email,
        created=now,
        last_updated=now,
        last_login=now
    )

    update_dict = {
        'email': stmt.excluded.email,
        'last_login': now,
        'last_updated': sqlalchemy.case(
            (sqlalchemy.and_(
                User.email != stmt.excluded.email,
                User.name != name
            ), stmt.excluded.last_updated),
            else_=User.last_updated
        )
    }

    if name:
        update_dict['name'] = name

    on_conflict_stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_=update_dict
    )
    db.execute(on_conflict_stmt)