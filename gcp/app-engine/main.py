from datetime import datetime
from functools import wraps
import firebase_admin
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
from slack_handler import handle_slack_command
from slack_sdk.errors import SlackApiError
import sqlalchemy
from auth_utils import validate_token, get_user_id_from_token
from db_utils import get_db_connection
from db_queries import DB_SCHEMA
from utils import json_serial
from league_queries import (
    get_leagues_for_user, get_league_by_id, create_league, update_league,
    get_league_members, join_league, create_invitation,
    get_user_picks, submit_picks, get_available_players,
    get_league_standings, get_tournament_scoring,
    get_user_favorites, add_favorite, delete_favorite
)

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

# Configure CORS for web app
CORS(app, resources={
    r"/api/*": {
        "origins": [
            os.getenv('WEB_APP_URL', 'http://localhost:5173'),
            "https://golf-better.web.app",
            "https://golf-better.firebaseapp.com",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"],
    }
})

firebase_admin.initialize_app()

PUBLIC_API_PREFIX = '/api/v1'
PRIVATE_API_PREFIX = '/protected/api/v1'

# Store processed event_ids with their timestamps
processed_slack_events = {}

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

    exception = None

    if 'challenge' in data:
        return jsonify(data['challenge'])

    # Deduplicate slack messages sent from Slack
    if data['event_id'] in processed_slack_events:
        print(f"Skipping duplicate slack event: {data}")
        return jsonify({'status': 'duplicate event'}), 200
    else:
        current_time = time.time()
        processed_slack_events[data['event_id']] = current_time

        # Cleanup event_ids older than 10 minutes
        expiration_time_secs = 600  # 10 minutes
        for event_id in list(processed_slack_events.keys()):
            if current_time - processed_slack_events[event_id] > expiration_time_secs:
                del processed_slack_events[event_id]

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
            print(f'Unknown event type: {event}')
        except Exception as ex:
            try:
                exception = ex
                msg = f'Error processing message: {data}. {ex}'
                if not os.getenv('NO_SLACK'):
                    slack_client.chat_postMessage(channel=channel, text=msg)
                else:
                    print(f"Would send error to slack: channel={channel}, text={msg}")
            except SlackApiError as e:
                exception = e
                print(f"Error posting message: {e.response['error']}")

    if not exception:
        print(f'Unknown type: {data}')

    if exception is not None:
        print(f"Error processing slack event: {data}", exception)
    else:
        print(f"Error processing slack event: {data}")
    return f"Error processing slack event: {data}", 400


# =============================================================================
# Fantasy League Endpoints
# =============================================================================

@app.route(PUBLIC_API_PREFIX + '/leagues', methods=['GET'])
@validate_token
def get_leagues(user_email):
    """Get all leagues the user is a member of, plus public leagues."""
    user_id = get_user_id_from_token()
    pool = get_db_connection()
    with pool.connect() as db_conn:
        leagues = get_leagues_for_user(db_conn, user_id)
        return json.dumps(leagues, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues', methods=['POST'])
@validate_token
def create_new_league(user_email):
    """Create a new fantasy league."""
    user_id = get_user_id_from_token()
    data = request.get_json(force=True)

    if not data or 'name' not in data:
        return json.dumps({"error": "League name is required"}), 400

    pool = get_db_connection()
    with pool.connect() as db_conn:
        league = create_league(
            db_conn,
            name=data['name'],
            owner_id=user_id,
            league_type=data.get('leagueType', 'season'),
            roster_config=data.get('rosterConfig', {'roster_size': 6, 'use_tiers': False, 'use_salary_cap': False}),
            scoring_config=data.get('scoringConfig', {}),
            pick_deadline_type=data.get('pickDeadlineType', 'tournament_start'),
            tournament_id=data.get('tournamentId'),
            is_public=data.get('isPublic', False),
        )
        return json.dumps(league, default=json_serial), 201


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>', methods=['GET'])
@validate_token
def get_league_detail(user_email, league_id):
    """Get league details."""
    user_id = get_user_id_from_token()
    pool = get_db_connection()
    with pool.connect() as db_conn:
        league = get_league_by_id(db_conn, league_id, user_id)
        if not league:
            return json.dumps({"error": "League not found"}), 404
        return json.dumps(league, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>', methods=['PUT'])
@validate_token
def update_league_settings(user_email, league_id):
    """Update league settings (owner only)."""
    user_id = get_user_id_from_token()
    data = request.get_json(force=True)

    pool = get_db_connection()
    with pool.connect() as db_conn:
        success = update_league(db_conn, league_id, user_id, data)
        if not success:
            return json.dumps({"error": "League not found or not authorized"}), 404
        league = get_league_by_id(db_conn, league_id, user_id)
        return json.dumps(league, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/members', methods=['GET'])
@validate_token
def get_members(user_email, league_id):
    """Get all members of a league."""
    pool = get_db_connection()
    with pool.connect() as db_conn:
        members = get_league_members(db_conn, league_id)
        return json.dumps(members, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/join', methods=['POST'])
@validate_token
def join_league_endpoint(user_email, league_id):
    """Join a league using invite code."""
    user_id = get_user_id_from_token()
    data = request.get_json(force=True)
    invite_code = data.get('inviteCode', '')

    pool = get_db_connection()
    with pool.connect() as db_conn:
        member = join_league(db_conn, league_id, user_id, invite_code)
        if not member:
            return json.dumps({"error": "Invalid invite code or already a member"}), 400
        return json.dumps(member, default=json_serial), 201


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/invite', methods=['POST'])
@validate_token
def invite_to_league_endpoint(user_email, league_id):
    """Send a league invitation."""
    user_id = get_user_id_from_token()
    data = request.get_json(force=True)
    email = data.get('email')

    if not email:
        return json.dumps({"error": "Email is required"}), 400

    pool = get_db_connection()
    with pool.connect() as db_conn:
        invitation = create_invitation(db_conn, league_id, email, user_id)
        return json.dumps(invitation, default=json_serial), 201


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/picks', methods=['GET'])
@validate_token
def get_picks_endpoint(user_email, league_id):
    """Get user's picks for a league."""
    user_id = get_user_id_from_token()
    tournament_id = request.args.get('tournamentId')

    pool = get_db_connection()
    with pool.connect() as db_conn:
        picks = get_user_picks(db_conn, league_id, user_id, tournament_id)
        return json.dumps(picks, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/picks', methods=['POST'])
@validate_token
def submit_picks_endpoint(user_email, league_id):
    """Submit picks for a tournament."""
    user_id = get_user_id_from_token()
    data = request.get_json(force=True)

    tournament_id = data.get('tournamentId')
    player_ids = data.get('playerIds', [])

    if not tournament_id:
        return json.dumps({"error": "Tournament ID is required"}), 400

    pool = get_db_connection()
    with pool.connect() as db_conn:
        picks = submit_picks(db_conn, league_id, user_id, tournament_id, player_ids)
        return json.dumps(picks, default=json_serial), 201


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/picks/<tournament_id>/available-players', methods=['GET'])
@validate_token
def get_available_players_endpoint(user_email, league_id, tournament_id):
    """Get players available for picking."""
    pool = get_db_connection()
    with pool.connect() as db_conn:
        players = get_available_players(db_conn, tournament_id)
        return json.dumps(players, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/standings', methods=['GET'])
@validate_token
def get_standings_endpoint(user_email, league_id):
    """Get league standings."""
    pool = get_db_connection()
    with pool.connect() as db_conn:
        standings = get_league_standings(db_conn, league_id)
        return json.dumps(standings, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/leagues/<league_id>/scoring/<tournament_id>', methods=['GET'])
@validate_token
def get_scoring_endpoint(user_email, league_id, tournament_id):
    """Get detailed scoring for a tournament."""
    pool = get_db_connection()
    with pool.connect() as db_conn:
        scoring = get_tournament_scoring(db_conn, league_id, tournament_id)
        return json.dumps(scoring, default=json_serial), 200


# =============================================================================
# Favorites Endpoints
# =============================================================================

@app.route(PUBLIC_API_PREFIX + '/favorites', methods=['GET'])
@validate_token
def get_favorites_endpoint(user_email):
    """Get user's favorites."""
    user_id = get_user_id_from_token()
    pool = get_db_connection()
    with pool.connect() as db_conn:
        favorites = get_user_favorites(db_conn, user_id)
        return json.dumps(favorites, default=json_serial), 200


@app.route(PUBLIC_API_PREFIX + '/favorites', methods=['POST'])
@validate_token
def add_favorite_endpoint(user_email):
    """Add a favorite."""
    user_id = get_user_id_from_token()
    data = request.get_json(force=True)

    favorite_type = data.get('favoriteType')
    target_id = data.get('targetId')

    if not favorite_type or not target_id:
        return json.dumps({"error": "favoriteType and targetId are required"}), 400

    pool = get_db_connection()
    with pool.connect() as db_conn:
        favorite = add_favorite(db_conn, user_id, favorite_type, target_id)
        return json.dumps(favorite, default=json_serial), 201


@app.route(PUBLIC_API_PREFIX + '/favorites/<favorite_id>', methods=['DELETE'])
@validate_token
def delete_favorite_endpoint(user_email, favorite_id):
    """Delete a favorite."""
    user_id = get_user_id_from_token()
    pool = get_db_connection()
    with pool.connect() as db_conn:
        success = delete_favorite(db_conn, favorite_id, user_id)
        if not success:
            return json.dumps({"error": "Favorite not found"}), 404
        return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

