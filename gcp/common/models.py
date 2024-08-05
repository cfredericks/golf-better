"""
Database data models
"""

from sqlalchemy import create_engine, Column, String, Date, Boolean, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PGATournament(Base):
    __tablename__ = 'pga_tournaments'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(Date)
    is_completed = Column(Boolean, nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return f"<PGATournament(id='{self.id}', name='{self.name}', start_date='{self.start_date}', is_completed={self.is_completed}, last_updated='{self.last_updated}')>"

    def __str__(self):
        return f"PGATournament(id='{self.id}', name='{self.name}', start_date='{self.start_date}', is_completed={self.is_completed}, last_updated='{self.last_updated}')"

class PGAPlayer(Base):
    __tablename__ = 'pga_players'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return f"<PGAPlayer(id='{self.id}', name='{self.name}', last_updated='{self.last_updated}')>"

    def __str__(self):
        return f"PGAPlayer(id='{self.id}', name='{self.name}', last_updated='{self.last_updated}')"

class PGALeaderboardPlayer(Base):
    __tablename__ = 'pga_leaderboard_players'
    id = Column(String, primary_key=True)
    tournament_id = Column(String, nullable=False)
    player_id = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return f"<PGALeaderboardPlayer(id='{self.id}', tournament_id='{self.tournament_id}', player_id='{self.player_id}', last_updated='{self.last_updated}')>"

    def __str__(self):
        return f"PGALeaderboardPlayer(id='{self.id}', tournament_id='{self.tournament_id}', player_id='{self.player_id}', last_updated='{self.last_updated}')"

class PGAPlayerScorecard(Base):
    __tablename__ = 'pga_player_scorecards'
    id = Column(String, primary_key=True)
    tournament_id = Column(String, nullable=False)
    player_id = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return f"<PGAPlayerScorecard(id='{self.id}', tournament_id='{self.tournament_id}', player_id='{self.player_id}', last_updated='{self.last_updated}')>"

    def __str__(self):
        return f"PGAPlayerScorecard(id='{self.id}', tournament_id='{self.tournament_id}', player_id='{self.player_id}', last_updated='{self.last_updated}')"

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created = Column(TIMESTAMP(timezone=True), nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return f"<User(id='{self.id}', name='{self.name}', email='{self.email}', created='{self.created}', last_updated='{self.last_updated}', last_login='{self.last_login}')>"

    def __str__(self):
        return f"User(id='{self.id}', name='{self.name}', email='{self.email}', created='{self.created}', last_updated='{self.last_updated}', last_login='{self.last_login}')"
