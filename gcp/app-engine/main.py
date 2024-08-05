from flask import Flask, jsonify, request
import json

from common.auth_utils import validate_token, PUBLIC_API_PREFIX, PRIVATE_API_PREFIX
from common.db import SessionLocal
from common.queries import get_tournaments, get_leaderboard_players, get_player_scorecards, upsert_user
from common.schemas import TournamentSchema, PlayerRowV3Schema, ScorecardV3Schema

app = Flask(__name__)

@app.route(PUBLIC_API_PREFIX + '/pga-tournaments', methods=['GET'])
@validate_token
def get_pga_tournaments(user_email):
    print(f"Got get_pga_tournaments request from user: {user_email}")
    tournament_id = request.args.get('tournamentId', None)
    db = SessionLocal()
    try:
        data = [t.data for t in get_tournaments(db, tournament_id)]
        schema = TournamentSchema(many=True)
        return jsonify(schema.dump(data)), 200
    except Exception as e:
        print(f'Error querying get_pga_tournaments tournament_id={tournament_id}: {e}', e)
        return json.dumps({"error": "Internal server error"}), 500
    finally:
        db.close()


@app.route(PUBLIC_API_PREFIX + '/pga-leaderboard-players', methods=['GET'])
@validate_token
def get_pga_leaderboard_players(user_email):
    print(f"Got get_pga_leaderboard_players request from user: {user_email}")
    id = request.args.get('id', None)
    tournament_id = request.args.get('tournamentId', None)
    player_id = request.args.get('id', None)
    db = SessionLocal()
    try:
        data = [t.data for t in get_leaderboard_players(db, id, player_id, tournament_id)]
        schema = PlayerRowV3Schema(many=True)
        return jsonify(schema.dump(data)), 200
    except Exception as e:
        print(f'Error querying get_pga_leaderboard_players id={id} tournament_id={tournament_id} player_id={player_id}: {e}', e)
        return json.dumps({"error": "Internal server error"}), 500
    finally:
        db.close()

@app.route(PUBLIC_API_PREFIX + '/pga-player-scorecards', methods=['GET'])
@validate_token
def get_pga_player_scorecards(user_email):
    print(f"Got get_pga_player_scorecards request from user: {user_email}")
    id = request.args.get('id', None)
    tournament_id = request.args.get('tournamentId', None)
    player_id = request.args.get('id', None)
    db = SessionLocal()
    try:
        data = [t.data for t in get_player_scorecards(db, id, player_id, tournament_id)]
        schema = ScorecardV3Schema(many=True)
        return jsonify(schema.dump(data)), 200
    except Exception as e:
        print(f'Error querying get_pga_player_scorecards id={id} tournament_id={tournament_id} player_id={player_id}: {e}', e)
        return json.dumps({"error": "Internal server error"}), 500
    finally:
        db.close()

@app.route(PUBLIC_API_PREFIX + '/users', methods=['POST'])
@validate_token
def post_user(user_email):
    print(f"Got post_user request from user: {user_email}")
    data = request.get_json(force=True)
    if data is None:
        return 'Post body empty', 400
    if 'email' not in data:
        return 'Post body must include email', 400

    id = data.get('id')
    name = data.get('name')
    email = data.get('email')

    try:
        db = SessionLocal()
        upsert_user(db, id, name, email)
        db.commit()
        print(f'Finished updating user id={id or email} email={email}')
    except Exception as e:
        db.rollback()
        print(f'Error updating user id={id or email} email={email}: {e}', e)
        return json.dumps({"error": "Internal server error"}), 500
    finally:
        db.close()

    return '', 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
