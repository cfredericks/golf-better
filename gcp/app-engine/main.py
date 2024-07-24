from flask import Flask, request
import os
import json
import requests
from datetime import date, datetime
from google.cloud.sql.connector import Connector
import sqlalchemy
from google.cloud import secretmanager
import pg8000
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

firebase_admin.initialize_app()

DEFAULT_PROJECT_ID = 'stoked-depth-428423-j7'
DEFAULT_VERSION_ID = 'latest'

PUBLIC_API_PREFIX = '/api/v1'
PRIVATE_API_PREFIX = '/protected/api/v1'

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print("Exception decoding auth token", e)
        return None

def get_gsm_secret(secret_id, project_id=DEFAULT_PROJECT_ID, version_id=DEFAULT_VERSION_ID):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    payload = response.payload.data.decode('UTF-8')
    return payload

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def get_db_connection():
    db_user = os.getenv('DB_USER', default='postgres')
    db_password = os.getenv('DB_PASSWORD', default=get_gsm_secret('golf-better-cloudsql-password'))
    db_name = os.getenv('DB_NAME', default='postgres')
    db_instance_conn_name = os.getenv('INSTANCE_CONNECTION_NAME', default='stoked-depth-428423-j7:us-central1:golf-better')
    db_host = os.getenv('DB_HOST', default=f'/cloudsql/{db_instance_conn_name}')
    db_port = os.getenv('DB_PORT', default=5432)

    pw_log = "****" if db_password is not None else "<unset>"
    print(f'Connecting to PG on user={db_user}, pw={pw_log}, host={db_host}, port={db_port}, db={db_name}')

    connector = Connector()
    def getconn():
        if db_instance_conn_name:
            return connector.connect(
                db_instance_conn_name,
                "pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
                #ip_type=IPTypes.PRIVATE
            )
        else:
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

@app.route(PUBLIC_API_PREFIX + '/pga-tournaments', methods=['GET'])
def get_pga_tournaments():
    decoded_token = None
    if 'Authorization' in request.headers:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        decoded_token = verify_id_token(id_token)
        print(decoded_token)
    if not decoded_token:
        return json.dumps({"error": "Unauthorized"}), 401
    user_email = decoded_token.get('email')
    print(f"Got request from user: {user_email}")

    query = "SELECT data FROM pga_tournaments where 1=1"
    tournament_id = request.args.get('id', None)
    if tournament_id is not None:
        query = query + " and id = '" + tournament_id + "'"
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return json.dumps([row[0] for row in records], default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/pga-leaderboard-players', methods=['GET'])
def get_pga_leaderboard_players():
    decoded_token = None
    if 'Authorization' in request.headers:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        decoded_token = verify_id_token(id_token)
    if not decoded_token:
        return json.dumps({"error": "Unauthorized"}), 401
    user_email = decoded_token.get('email')
    print(f"Got request from user: {user_email}")

    query = "SELECT data FROM pga_leaderboard_players where 1=1"
    tournament_id = request.args.get('tournamentId', None)
    if tournament_id is not None:
        query = query + " and tournament_id = '" + tournament_id + "'"
    player_id = request.args.get('id', None)
    if player_id is not None:
        query = query + " and id = '" + player_id + "'"
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return json.dumps([row[0] for row in records], default=json_serial), 200

@app.route(PUBLIC_API_PREFIX + '/pga-player-scorecards', methods=['GET'])
def get_pga_player_scorecards():
    decoded_token = None
    if 'Authorization' in request.headers:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        decoded_token = verify_id_token(id_token)
    if not decoded_token:
        return json.dumps({"error": "Unauthorized"}), 401
    user_email = decoded_token.get('email')
    print(f"Got request from user: {user_email}")

    query = "SELECT data FROM pga_player_scorecards where 1=1"
    tournament_id = request.args.get('tournamentId', None)
    if tournament_id is not None:
        query = query + " and tournament_id = '" + tournament_id + "'"
    player_id = request.args.get('id', None)
    if player_id is not None:
        query = query + " and id = '" + player_id + "'"
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return json.dumps([row[0] for row in records], default=json_serial), 200

@app.route(PRIVATE_API_PREFIX + '/refreshTournaments', methods=['POST'])
def refresh_tournaments():
    decoded_token = None
    if 'Authorization' in request.headers:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        decoded_token = verify_id_token(id_token)
    if not decoded_token:
        return json.dumps({"error": "Unauthorized"}), 401
    user_email = decoded_token.get('email')
    print(f"Got request from user: {user_email}")

    print("Querying Tournaments API...")
    sports_data_api_key = get_gsm_secret('sports-data-api-key')
    tournaments_response = requests.get("https://api.sportsdata.io/golf/v2/json/Tournaments?key=" + sports_data_api_key)
    tournaments = tournaments_response.json()
    print("Got response: ")# + json.dumps(tournaments))

    last_updated = datetime.utcnow()
    tournaments_by_name_startDate = {}
    for t in tournaments:
        tournaments_by_name_startDate[(t['Name'], t['StartDate'])] = (
                t["TournamentID"],
                "'" + t["Name"].replace("'", "''") + "'",
                "'" + t["StartDate"] + "'" if t["StartDate"] is not None else None,
                "'" + t["EndDate"] + "'" if t["EndDate"] is not None else None,
                "'" + str(last_updated) + "'",
                "'" + json.dumps(t).replace("'", "''") + "'"
            )

    pool = get_db_connection()
    with pool.connect() as db_conn:
        try:
            args_str = ','.join([f'({t[0]}, {t[1]}, {t[2]}, {t[3]}, {t[4]}, {t[5]})' for t in tournaments_by_name_startDate.values()])
            #print(args_str)
            db_conn.execute(sqlalchemy.text("INSERT INTO tournaments (id, name, start_date, end_date, last_updated, data) VALUES " \
                + args_str \
                + "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, last_updated = EXCLUDED.last_updated, data = EXCLUDED.data"))

            # commit transaction (SQLAlchemy v2.X.X is commit as you go)
            db_conn.commit()
            print("Finished refreshing tournaments")
            return '', 200
        except Exception as e:
            print("Error writing to DB: ", e)
            raise e
            return '', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

