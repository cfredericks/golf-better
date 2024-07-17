import functions_framework
import os
import json
import requests
from datetime import datetime as dt
from google.cloud.sql.connector import Connector
import sqlalchemy
from google.cloud import secretmanager
from threading import Thread

def get_gsm_secret(secret_id, project_id='stoked-depth-428423-j7', version_id='latest'):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    payload = response.payload.data.decode('UTF-8')
    return payload

def get_db_connection():
    db_user = os.getenv('DB_USER', default='postgres')
    db_password = os.getenv('DB_PASSWORD', default=get_gsm_secret('golf-better-cloudsql-password'))
    db_name = os.getenv('DB_NAME', default='postgres')
    db_instance_conn_name = os.getenv('INSTANCE_CONNECTION_NAME', default='stoked-depth-428423-j7:us-central1:golf-better')
    db_host = os.getenv('DB_HOST', default=f'/cloudsql/{db_instance_conn_name}')

    pw_log = "****" if db_password is not None else "<unset>"
    print(f'Connecting to PG on user={db_user}, pw={pw_log}, host={db_host}, db={db_name}')

    connector = Connector()
    def getconn():
        conn = connector.connect(
            db_instance_conn_name,
            "pg8000",
            user=db_user,
            password=db_password,
            db=db_name
        )
        return conn

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        connect_args={'timeout': 180}
    )

    return pool


@functions_framework.http
def refresh_leaderboards(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    sports_data_api_key = get_gsm_secret('sports-data-api-key')

    lookback_days = 7
    process_all = False
    if request is not None:
        request_json = request.get_json(silent=True, force=True)
        if request_json is not None:
            process_all = str(request_json.get('processAll', process_all)).lower() == 'true'
            if not process_all:
                lookback_days = int(request_json.get('lookbackDays', lookback_days))

    pool = get_db_connection()

    condition = 'All'
    if not process_all:
      condition = f"Lookback {lookback_days} Days"
    print(f"Loading Tournament IDs ({condition})...")
    with pool.connect() as db_conn:
        where_clause = '' if process_all else f" where start_date >= (current_date - interval '{lookback_days}' day)"
        tournament_ids = [row[0] for row in db_conn.execute(sqlalchemy.text(f"select id from tournaments{where_clause};")).fetchall()]

    def processLeaderboard(tournament_id, results, i, pool):
        print(f'Querying leaderboard for tournament {tournament_id}...')
        leaderboard_response = requests.get(f"https://api.sportsdata.io/golf/v2/json/Leaderboard/{tournament_id}?key=" + sports_data_api_key)
        if leaderboard_response.status_code != 200 :
            print(f"No leaderboard leaderboard for tournament {tournament_id}")
            results[i] = True
            return
        leaderboard = leaderboard_response.json()
        if not leaderboard['Players']:
            print(f"No players on leaderboard for tournament {tournament_id}")
            results[i] = True
            return
        print(f"Got leaderboard response for tournament {tournament_id}")# + json.dumps(tournaments))

        last_updated = dt.utcnow()
        players_by_tournament_player_id = {}
        for p in leaderboard['Players']:
            players_by_tournament_player_id[(p['PlayerTournamentID'])] = (
                    p["PlayerTournamentID"],
                    p["TournamentID"],
                    p["PlayerID"],
                    "'" + p["Name"].replace("'", "''") + "'",
                    "'" + str(last_updated) + "'",
                    "'" + json.dumps(p).replace("'", "''") + "'"
                )

        with pool.connect() as db_conn:
            try:
                args_str = ','.join([f'({t[0]}, {t[1]}, {t[2]}, {t[3]}, {t[4]}, {t[5]})' for t in players_by_tournament_player_id.values()])
                #print(args_str)
                db_conn.execute(sqlalchemy.text("INSERT INTO tournament_players (id, tournament_id, player_id, name, last_updated, data) VALUES " \
                    + args_str \
                    + " ON CONFLICT (id) DO UPDATE SET tournament_id = EXCLUDED.tournament_id, player_id = EXCLUDED.player_id, name = EXCLUDED.name, last_updated = EXCLUDED.last_updated, data = EXCLUDED.data"))

                db_conn.commit()
                print(f"Finished refreshing leaderboard for tournament {tournament_id}")
                results[i] = True
            except Exception as e:
                print(f"Error writing to DB for tournament {tournament_id}: ", e)
                results[i] = False

    print(f"Querying Leaderboard API for {len(tournament_ids)} tournaments...")

    # multithreading (issues with pickling child functions)
    #with Pool(10) as p:
    #    results = p.starmap(processLeaderboard, [(tid, pool) for tid in tournament_ids])

    # multiprocess (ugly)
    #m = mp.Process(target=processLeaderboard, args=[(tid, pool) for tid in tournament_ids])
    #m.start()
    #print("here is main", os.getpid())
    #m.join()

    # threading
    results = [False] * len(tournament_ids)
    thread_list = []
    for i in range(len(tournament_ids)):
        t = Thread(target=processLeaderboard, args=(tournament_ids[i], results, i, pool))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()

    for res in results:
        if not res:
            return '', 500

    return '', 200

# For running locally
if __name__ == '__main__':
    refresh_leaderboards(None)
