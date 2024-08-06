import factory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from your_application.models import PGATournament, PGAPlayer, PGALeaderboardPlayer, PGAPlayerScorecard, User

# Assuming `engine` is your SQLAlchemy engine
Session = sessionmaker(bind=engine)
session = Session()

class PGATournamentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PGATournament
        sqlalchemy_session = session  # the SQLAlchemy session object

    id = factory.Faker('uuid4')
    name = factory.Faker('word')
    start_date = factory.Faker('date')
    is_completed = factory.Faker('boolean')
    data = factory.Faker('json')
    last_updated = factory.LazyFunction(datetime.utcnow)

class PGAPlayerFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PGAPlayer
        sqlalchemy_session = session

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    data = factory.Faker('json')
    last_updated = factory.LazyFunction(datetime.utcnow)

class PGALeaderboardPlayerFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PGALeaderboardPlayer
        sqlalchemy_session = session

    id = factory.Faker('uuid4')
    tournament_id = factory.Faker('uuid4')
    player_id = factory.Faker('uuid4')
    data = factory.Faker('json')
    last_updated = factory.LazyFunction(datetime.utcnow)

class PGAPlayerScorecardFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PGAPlayerScorecard
        sqlalchemy_session = session

    id = factory.Faker('uuid4')
    tournament_id = factory.Faker('uuid4')
    player_id = factory.Faker('uuid4')
    data = factory.Faker('json')
    last_updated = factory.LazyFunction(datetime.utcnow)

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = session

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    email = factory.Faker('email')
    created = factory.LazyFunction(datetime.utcnow)
    last_updated = factory.LazyFunction(datetime.utcnow)
    last_login = factory.LazyFunction(datetime.utcnow)
