import os
from google.cloud.sql.connector import Connector #, IPTypes
import sqlalchemy
import pg8000
from auth_utils import get_gsm_secret
from datetime import datetime

DB_SCHEMA = 'golfbetter'

def get_db_connection():
    db_user = os.getenv('DB_USER', default='postgres')
    db_password = os.getenv('DB_PASSWORD') or get_gsm_secret('golf-better-cloudsql-password')
    db_name = os.getenv('DB_NAME', default='postgres')
    db_instance_conn_name = os.getenv('INSTANCE_CONNECTION_NAME', default='stoked-depth-428423-j7:us-central1:golf-better')
    db_host = os.getenv('DB_HOST', default=f'/cloudsql/{db_instance_conn_name}')
    db_port = os.getenv('DB_PORT', default=5432)

    pw_log = "****" if db_password is not None else "<unset>"
    print(f'Connecting to PG on user={db_user}, pw={pw_log}, host={db_host}, port={db_port}, db={db_name}')

    def getconn():
        if db_instance_conn_name:
            print(f'Connecting to CloudSQL instance with instance name: "{db_instance_conn_name}"')
            connector = Connector()
            return connector.connect(
                db_instance_conn_name,
                "pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
                #ip_type=IPTypes.PRIVATE
            )
        else:
            print('Connecting to vanilla Postgres database')
            return pg8000.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        connect_args={
            "port": db_port
        }
    )

    return pool

def get_next_tournaments(tournament_search=None):
    query = f"""
        select *
        from
        (
          select name,
            start_date,
            is_completed,
            data->>'date' as date,
            data->>'city' as city,
            coalesce(data->>'stateCode', '') as stateCode,
            data->>'countryCode' as countryCode
          from {DB_SCHEMA}.pga_tournaments
          where ({f"lower(id) like '%{str(tournament_search).lower()}%' or lower(name) like '%{str(tournament_search).lower()}%'" if tournament_search is not None else "1=1"})
          order by is_completed, abs(EXTRACT(EPOCH FROM (NOW() - start_date)))
          limit {1 if tournament_search is not None else 5}
        )
        order by start_date
    """
    pool = get_db_connection()
    now = datetime.now()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        tournaments = [{
            "name": row[0],
            "location": row[4] + (", " + row[5] + ' ' if row[5] else ' '),
            "date": row[3],
            "status": "Done" if row[2] else "Scheduled" if now.date() < row[1] else "In Progress"
        } for row in records]
        if len(tournaments) == 1:
            return tournaments[0]
        return tournaments

def get_player(player_search, tournament_search, round=None):
    tournament_filter = f"lower(t.id) like '%{str(tournament_search).lower()}%' or lower(t.name) like '%{str(tournament_search).lower()}%'"
    player_filter = f"lower(sc.player_id) like '%{str(player_search).lower()}%' or lower(sc.data->'player'->>'displayName') like '%{str(player_search).lower()}%'"
    query = f"""
        with latest_tournament as (
          select id, name
          from {DB_SCHEMA}.pga_tournaments t
          where (lower(t.id) like '%wyndh%' or lower(t.name) like '%wyndh%')
          order by t.is_completed, abs(EXTRACT(EPOCH FROM (NOW() - t.start_date)))
          limit 1
        )
        select sc.data->'player'->>'displayName' as name,
          t.name as tournamentName,
          sc.data->'roundScores'
        from {DB_SCHEMA}.pga_player_scorecards sc
        inner join latest_tournament t on sc.tournament_id = t.id
        where (({tournament_filter}) and ({player_filter}))
        limit 1
    """
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        if len(records) != 1:
            return None
        row = records[0]
        round_scores = row[2]
        if not round_scores:
            return None
        scores = round_scores[round - 1] if round else round_scores[-1]
        par = []
        score = []
        for hole in scores['firstNine']['holes']:
            par.append((hole['par'], hole['holeNumber']))
            score.append((hole['score'], hole['holeNumber']))
        for hole in scores['secondNine']['holes']:
            par.append((hole['par'], hole['holeNumber']))
            score.append((hole['score'], hole['holeNumber']))
        par.sort(key=lambda x: x[1])
        score.sort(key=lambda x: x[1])
        return {
            "name": row[0],
            "tournament_name": row[1],
            "pars": [p[0] for p in par],
            "scores": [s[0] for s in score],
            "round": round if round else len(round_scores)
        }

def get_top_players(tournament_search, limit=10):
    tournament_filter = f"lower(t.id) like '%{str(tournament_search).lower()}%' or lower(t.name) like '%{str(tournament_search).lower()}%'"
    query = f"""
        with latest_tournament as (
          select id, name
          from golfbetter.pga_tournaments t
          where ({tournament_filter})
          order by t.is_completed, abs(EXTRACT(EPOCH FROM (NOW() - t.start_date)))
          limit 1
        )
        select p.data->'player'->>'displayName' as name,
          p.data->'scoringData'->>'total' as score,
          p.data->'scoringData'->>'position' as position
        from golfbetter.pga_leaderboard_players p
        where p.tournament_id in (select t.id from latest_tournament t)
        order by (p.data->'scoringData'->>'totalSort')::int
        limit {limit}
    """
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return [{
            "name": row[0],
            "score": row[1],
            "rank": row[2]
        } for row in records]