if __name__ != '__main__':
    import functions_framework
else:
    functions_framework = lambda: None
    functions_framework.http = None

import os
import json
import requests
from datetime import datetime as dt
from google.cloud.sql.connector import Connector
import sqlalchemy
from google.cloud import secretmanager

# Conditionally apply the "dec" decorator based on the "cond" conditional
def conditionally(dec, cond):
    def resdec(f):
        if not cond:
            return f
        return dec(f)
    return resdec

def get_gsm_secret(secret_id, project_id='stoked-depth-428423-j7', version_id='latest'):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    payload = response.payload.data.decode('UTF-8')
    return payload

sports_data_api_key = get_gsm_secret('sports-data-api-key')

db_user = os.getenv('DB_USER', default='postgres')
db_password = os.getenv('DB_PASSWORD', default=get_gsm_secret('golf-better-cloudsql-password'))
db_name = os.getenv('DB_NAME', default='postgres')
db_instance_conn_name = os.getenv('INSTANCE_CONNECTION_NAME', default='stoked-depth-428423-j7:us-central1:golf-better')
db_host = os.getenv('DB_HOST', default=f'/cloudsql/{db_instance_conn_name}')

def get_db_connection():
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
    )

    return pool


@conditionally(functions_framework.http, __name__ != '__main__')
def refresh_tournaments(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    #request_json = request.get_json(silent=True)
    #request_args = request.args

    print("Querying /Tournaments API...")
    tournaments_response = requests.get("https://api.sportsdata.io/golf/v2/json/Tournaments?key=" + sports_data_api_key)
    tournaments = tournaments_response.json()
    print("Got response: ")# + json.dumps(tournaments))

    last_updated = dt.utcnow()
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
            result = db_conn.execute(sqlalchemy.text("INSERT INTO tournaments (id, name, start_date, end_date, last_updated, data) VALUES " \
                + args_str \
                + "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, last_updated = EXCLUDED.last_updated, data = EXCLUDED.data"))

            db_conn.commit()
            print("Finished refreshing tournaments")
            return '', 200
        except Exception as e:
            print("Error writing to DB: ", e)
            raise e
            return '', 500

# For running locally
if __name__ == '__main__':
    refresh_tournaments(None)
