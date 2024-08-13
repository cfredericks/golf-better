from datetime import datetime
from functools import wraps
import firebase_admin
from flask import Flask, request, jsonify
import json
import os
from slack_handler import handle_slack_command
from slack_sdk.errors import SlackApiError
import sqlalchemy
from auth_utils import validate_token
from db_utils import get_db_connection, DB_SCHEMA
from utils import json_serial

if not os.getenv('NO_SLACK'):
    from slack_utils import slack_client, verify_slack_signature
else:
    # NOP decorator
    def verify_slack_signature(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function

app = Flask(__name__)

firebase_admin.initialize_app()

PUBLIC_API_PREFIX = '/api/v1'
PRIVATE_API_PREFIX = '/protected/api/v1'

@app.route(PUBLIC_API_PREFIX + '/pga-tournaments', methods=['GET'])
@validate_token
def get_pga_tournaments(user_email):
    print(f"Got get_pga_tournaments request from user: {user_email}")
    query = f"SELECT data FROM {DB_SCHEMA}.pga_tournaments where 1=1"
    tournament_id = request.args.get('id', None)
    if tournament_id is not None:
        query = query + " and id = '" + str(tournament_id) + "'"
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return json.dumps([row[0] for row in records], default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/pga-leaderboard-players', methods=['GET'])
@validate_token
def get_pga_leaderboard_players(user_email):
    print(f"Got get_pga_leaderboard_players request from user: {user_email}")
    query = f"SELECT data FROM {DB_SCHEMA}.pga_leaderboard_players where 1=1"
    tournament_id = request.args.get('tournamentId', None)
    if tournament_id is not None:
        query = query + " and tournament_id = '" + str(tournament_id) + "'"
    player_id = request.args.get('id', None)
    if player_id is not None:
        query = query + " and id = '" + str(player_id) + "'"
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return json.dumps([row[0] for row in records], default=json_serial), 200

@app.route(PUBLIC_API_PREFIX + '/pga-player-scorecards', methods=['GET'])
@validate_token
def get_pga_player_scorecards(user_email):
    print(f"Got get_pga_player_scorecards request from user: {user_email}")
    query = f"SELECT data FROM {DB_SCHEMA}.pga_player_scorecards where 1=1"
    tournament_id = request.args.get('tournamentId', None)
    if tournament_id is not None:
        query = query + " and tournament_id = '" + str(tournament_id) + "'"
    player_id = request.args.get('id', None)
    if player_id is not None:
        query = query + " and id = '" + str(player_id) + "'"
    pool = get_db_connection()
    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text(query)).fetchall()
        return json.dumps([row[0] for row in records], default=json_serial), 200

@app.route(PUBLIC_API_PREFIX + '/users', methods=['POST'])
@validate_token
def post_user(user_email):
    print(f"Got post_user request from user: {user_email}")
    data = request.get_json(force=True)
    if data is None:
        return 'Post body empty', 400
    if 'email' not in data:
        return 'Post body must include email', 400

    email = data.get('email').replace("'", "''")
    id = data.get('id')
    name = data.get('name')
    now = datetime.utcnow()
    if id:
        id = id.replace("'", "''")
    if name:
        name = name.replace("'", "''")

    on_conflict_updates = [
        "email = EXCLUDED.email",
        f"last_login = '{str(now)}'",
        # Use the actual name instead of EXCLUDED.name since EXCLUDED.name could be the email
        f"last_updated = (case when users.email != EXCLUDED.email or users.name != '{name}' then EXCLUDED.last_updated else users.last_updated end)"
    ]
    if name:
        # Use the actual name instead of EXCLUDED.name since EXCLUDED.name could be the email
        on_conflict_updates.append(f"name = '{name}'")

    pool = get_db_connection()
    with pool.connect() as db_conn:
        db_conn.execute(sqlalchemy.text(f'''
            insert into {DB_SCHEMA}.users (id, name, email, created, last_updated, last_login)
            values ('{id or email}', '{name or email}', '{email}', '{str(now)}', '{str(now)}', '{str(now)}')
            on conflict (id) do update set {", ".join(on_conflict_updates)}
            '''))
        db_conn.commit()
        print(f'Finished updating user id={id or email} email={email}')

    return '', 201

@app.route(PUBLIC_API_PREFIX + '/slack/events', methods=['POST'])
@verify_slack_signature
def post_slack_events(user_email=None):
    data = request.get_json(force=True)
    print(f"Got post_slack_events request from user: {user_email}: {data}")
    if data is None:
        print(f"Empty post body for request: {request}")
        return 'Post body empty', 400

    if 'challenge' in data:
        return jsonify(data['challenge'])

    if 'event' in data:
        event = data['event']
        channel = event['channel']
        try:
            print(f"Slack event received: {event}")
            if event['type'] == 'message' and 'bot_id' not in event:
                text = event['text']
                print(f"Slack message event sent from bot '{event['user']}' for channel '{channel}': '{text}'")
                return handle_slack_command(text, channel)
            if event['type'] == 'app_mention' and 'text' in event:
                text = event['text']
                print(f"Slack app_mention event sent from bot '{event['user']}' for channel '{channel}': '{text}'")
                return handle_slack_command(text, channel)
        except Exception as ex:
            try:
                msg = f'Error processing message: {data}. {ex}'
                slack_client.chat_postMessage(channel=channel, text=msg)
            except SlackApiError as e:
                print(f"Error posting message: {e.response['error']}")

    print(f"Error processing slack slack event: {data}")
    return f"Error processing slack slack event: {data}", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

