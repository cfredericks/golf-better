from functools import wraps
from flask import Flask, abort, jsonify, request
import hashlib
import hmac
import os
import json
import time
from datetime import date, datetime
from google.cloud.sql.connector import Connector #, IPTypes
import sqlalchemy
from google.cloud import secretmanager
import pg8000
import firebase_admin
from firebase_admin import auth
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

firebase_admin.initialize_app()

DEFAULT_PROJECT_ID = 'stoked-depth-428423-j7'
DEFAULT_VERSION_ID = 'latest'

PUBLIC_API_PREFIX = '/api/v1'
PRIVATE_API_PREFIX = '/protected/api/v1'

# Decorator to parse auth token and extract user email
def validate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        decoded_token = None
        if 'Authorization' in request.headers:
            id_token = request.headers.get('Authorization').split('Bearer ')[1]
            try:
                decoded_token = auth.verify_id_token(id_token)
            except Exception as e:
                print("Exception decoding auth token", e)
                return json.dumps({"error": "Unauthorized"}), 401

        if not decoded_token:
            return json.dumps({"error": "Unauthorized"}), 401

        user_email = decoded_token.get('email')
        return f(user_email, *args, **kwargs)
    return decorated_function

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

def verify_slack_signature(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        slack_signature = request.headers.get('X-Slack-Signature')
        slack_request_timestamp = request.headers.get('X-Slack-Request-Timestamp')

        # Protect against replay attacks
        if abs(time.time() - float(slack_request_timestamp)) > 60 * 5:
            return jsonify({'error': 'Request timestamp out of range'}), 400

        # Create the basestring
        sig_basestring = f'v0:{slack_request_timestamp}:{request.get_data(as_text=True)}'

        # Hash the basestring using your signing secret
        my_signature = 'v0=' + hmac.new(
            bytes(SLACK_SIGNING_SECRET, 'utf-8'),
            bytes(sig_basestring, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Compare the generated signature to the one in the request header
        if not hmac.compare_digest(my_signature, slack_signature):
            abort(400, 'Invalid request signature')

        return f(*args, **kwargs)

    return decorated_function

@app.route(PUBLIC_API_PREFIX + '/pga-tournaments', methods=['GET'])
#@validate_token
def get_pga_tournaments(user_email=None):
    print(f"Got get_pga_tournaments request from user: {user_email}")
    query = "SELECT data FROM golfbetter.pga_tournaments where 1=1"
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
    query = "SELECT data FROM golfbetter.pga_leaderboard_players where 1=1"
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
    query = "SELECT data FROM golfbetter.pga_player_scorecards where 1=1"
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
            insert into golfbetter.users (id, name, email, created, last_updated, last_login)
            values ('{id or email}', '{name or email}', '{email}', '{str(now)}', '{str(now)}', '{str(now)}')
            on conflict (id) do update set {", ".join(on_conflict_updates)}
            '''))
        db_conn.commit()
        print(f'Finished updating user id={id or email} email={email}')

    return '', 201



def handle_slack_event(data, channel, event_txt):
    type_field = 'dataType'
    if not event_txt.startswith(f'{type_field}='):
        return 'Missing required param: ''dataType''', 400

    all_data_types = ['tournaments', 'leaderboardPlayers', 'playerScorecards']
    data_type = event_txt[(len(type_field) + 1):]  # add 1 to include equals sign
    result = None
    if data_type == 'tournaments':
        result, _ = get_pga_tournaments()
    elif data_type == 'leaderboardPlayers':
        result, _ = get_pga_leaderboard_players()
    elif data_type == 'playerScorecards':
        result, _ =  get_pga_player_scorecards()
    else:
        str = f"Unknown dataType '{data_type}', allowed dataTypes: {all_data_types}"
        print(str)
        return str, 404

    if result is not None:
        try:
            slack_client.chat_postMessage(channel=channel, text=json.dumps(result))
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")

    str = f"Could not parse slack message: {data}"
    print(str)
    return str, 404

# Slack configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN") or get_gsm_secret('golfbetter-api-slackbot-token')
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET") or get_gsm_secret('golfbetter-api-slackbot-signing-secret')
slack_client = WebClient(token=SLACK_BOT_TOKEN)

def create_golf_scorecard_image(scores):
    # Image dimensions
    width = 800
    height = 80  # Adjust the height to fit the additional row for par values
    cell_width = width // 18
    cell_height = height

    # Create a blank image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Define colors and shapes
    green = (34, 139, 34)  # Green for birdies
    blue = (30, 144, 255)  # Blue for bogeys
    black = (0, 0, 0)      # Black for text

    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    # Draw the grid, hole numbers, par values, and scores
    for i in range(18):
        x0 = i * cell_width
        y0 = 0
        x1 = x0 + cell_width
        y1 = cell_height

        # Draw vertical grid lines
        draw.line([(x0, 0), (x0, height)], fill=black, width=2)
        draw.line([(x1, 0), (x1, height)], fill=black, width=2)

        # Draw the hole number
        hole_text = f"Hole {i + 1}"
        text_bbox = draw.textbbox((0, 0), hole_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x0 + cell_width / 2 - text_width / 2
        text_y = y0 + 5 - text_height / 2
        draw.text((text_x, text_y), hole_text, fill=black, font=font)

        # Draw the horizontal grid line underneath the hole number text
        draw.line([(x0, text_y + text_height + 5), (x1, text_y + text_height + 5)], fill=black, width=2)

        # Draw the par value
        par_text = f"Par {scores[i]['par']}"
        text_bbox = draw.textbbox((0, 0), par_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x0 + cell_width / 2 - text_width / 2
        text_y = y0 + 25 - text_height / 2  # Positioned below the hole number
        draw.text((text_x, text_y), par_text, fill=black, font=font)

        # Draw the horizontal grid line underneath the par value text
        draw.line([(x0, text_y + text_height + 5), (x1, text_y + text_height + 5)], fill=black, width=2)

        # Calculate the result based on par and shots
        score = scores[i]
        shots = score['shots']
        par = score['par']
        if shots < par:
            result = "birdie"
        elif shots > par:
            result = "bogey"
        else:
            result = "par"

        score_text = str(shots)

        # Calculate the text size
        text_bbox = draw.textbbox((0, 0), score_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate centered position
        shape_center_x = x0 + cell_width / 2
        shape_center_y = y0 + 55  # Adjust the center of the grid square for scores
        text_x = shape_center_x - text_width / 2
        text_y = shape_center_y - text_height / 2

        if result == "birdie":  # Birdie or better
            draw.ellipse([shape_center_x - 10, shape_center_y - 10, shape_center_x + 10, shape_center_y + 10], outline=green, width=2)
            draw.text((text_x, text_y), score_text, fill=black, font=font)

        elif result == "bogey":  # Bogey or worse
            draw.rectangle([shape_center_x - 10, shape_center_y - 10, shape_center_x + 10, shape_center_y + 10], outline=blue, width=2)
            draw.text((text_x, text_y), score_text, fill=black, font=font)

        else:  # Par
            draw.text((text_x, text_y), score_text, fill=black, font=font)

    # Draw the final horizontal line at the bottom
    draw.line([(0, height), (width, height)], fill=black, width=2)

    return image

def upload_image(channel, image_path):
    try:
        print("Uploading image...")
        response = slack_client.files_upload_v2(
            channels=channel,
            file=image_path,
            title="Golf Scorecard",
            initial_comment="Here is the golf scorecard:"
        )
        print("Done uploading image")
    except Exception as e:
        print("Error uploading image", e)

def handle_slack_command(command_text, channel):
    command_text = command_text.lower()

    # Handle tournament info command
    if "tournament info" in command_text:
        handle_tournament_info(command_text, channel)

    # Handle player info command
    elif "player info image" in command_text:
        # Example usage
        scores = [
            {"shots": 4, "par": 4},
            {"shots": 3, "par": 4},
            {"shots": 5, "par": 4},
            {"shots": 5, "par": 4},
            {"shots": 4, "par": 4},
            {"shots": 4, "par": 4},
            {"shots": 3, "par": 3},
            {"shots": 4, "par": 4},
            {"shots": 5, "par": 4},
            {"shots": 4, "par": 4},
            {"shots": 3, "par": 3},
            {"shots": 3, "par": 4},
            {"shots": 5, "par": 4},
            {"shots": 4, "par": 4},
            {"shots": 4, "par": 4},
            {"shots": 3, "par": 3},
            {"shots": 4, "par": 4},
            {"shots": 5, "par": 5},
        ]

        # Create the image
        print("Creating image...")
        try:
            image = create_golf_scorecard_image(scores)
        except Exception as e:
            print("Error creating image", e)
        print("Done creating image")

        # Save the image
        image_path = "/tmp/golf_scorecard.png"
        image.save(image_path)

        # Upload the image to Slack
        upload_image(channel, image_path)

    # Handle player info command
    elif "player info" in command_text:
        handle_player_info(command_text, channel)

    # Handle top 10 players command
    elif "top 10" in command_text:
        handle_top_10_players(command_text, channel)

    # Handle unknown command
    else:
        slack_client.chat_postMessage(
            channel=channel,
            text="Sorry, I didn't understand that command. Please try 'tournament info', 'player info image', 'player info', or 'top 10'" +
                 " (NOTE: for these test endpoints, the only supported player is 'tiger', and the only supported tournament is 'masters'."
        )

def handle_tournament_info(command_text, channel):
    # Parse for specific tournament ID or name
    words = command_text.split()
    if len(words) > 2:
        tournament_id = words[-1]  # Assume the last word is the ID
        tournament = get_tournament_details(tournament_id)
        if tournament:
            response_text = (
                f"*{tournament['name']}*:\n"
                f"Location: {tournament['location']}\n"
                f"Date: {tournament['date']}\n"
                f"Status: {tournament['status']}\n"
                f"Start Time: {tournament['start_time']}\n"
            )
        else:
            response_text = "Tournament not found."
    else:
        tournaments = get_tournaments()
        response_text = "*Tournaments:*\n"
        for tournament in tournaments:
            response_text += f"- {tournament['name']} ({tournament['status']})\n"

    slack_client.chat_postMessage(
        channel=channel,
        text=response_text
    )

def handle_player_info(command_text, channel):
    # Parse for specific player name/id and tournament name/id
    words = command_text.split()
    if len(words) > 3:
        player_name = words[-2]  # Assume second last word is player name/id
        tournament_id = words[-1]  # Assume the last word is the tournament id

        player_info = get_player_info(player_name, tournament_id)
        if player_info:
            response_text = (
                f"*{player_info['name']}* in *{player_info['tournament_name']}*:\n"
                f"Scores:\n"
                f"{format_scores_grid(player_info['pars'], player_info['scores'])}"
            )
        else:
            response_text = "Player or tournament not found."
    else:
        response_text = "Please specify both a player and a tournament."

    slack_client.chat_postMessage(
        channel=channel,
        text=response_text
    )

def handle_top_10_players(command_text, channel):
    words = command_text.split()
    if len(words) > 3:
        tournament_id = words[-1]  # Assume the last word is the tournament id
        top_10_players = get_top_10_players(tournament_id)
        if top_10_players:
            response_text = "*Top 10 Players:*\n"
            for player in top_10_players:
                response_text += (
                    f"{player['rank']}. {player['name']} - Score: {player['score']}\n"
                )
        else:
            response_text = "Tournament not found."
    else:
        response_text = "Please specify a tournament."

    slack_client.chat_postMessage(
        channel=channel,
        text=response_text
    )

def format_scores_grid(pars, scores):
    grid = "```\n"
    grid += " Hole  |" + "|".join([" " + str(i).ljust(3) for i in range(1, 19)]) + "|\n"
    grid += "-------|" + "|".join(["----" for _ in range(1, 19)]) + "|\n"
    grid += " Par   |" + "|".join([" " + str(par).ljust(3) for par in pars]) + "|\n"
    grid += "-------|" + "|".join(["----" for _ in range(1, 19)]) + "|\n"
    grid += " Score |" + "|".join([" " + str(score).ljust(3) for score in scores]) + "|\n```"
    return grid

# Mock functions to simulate data retrieval
def get_tournaments():
    # Replace with actual data retrieval logic
    return [
        {"name": "The Masters", "location": "Augusta", "date": "April 7-10", "status": "Scheduled"},
        {"name": "The Open Championship", "location": "St Andrews", "date": "July 14-17", "status": "Scheduled"}
    ]

def get_tournament_details(tournament_id):
    # Replace with actual data retrieval logic
    if tournament_id == "masters":
        return {
            "name": "The Masters",
            "location": "Augusta",
            "date": "April 7-10",
            "status": "Scheduled",
            "start_time": "8:00 AM"
        }
    return None

def get_player_info(player_name, tournament_id):
    # Replace with actual data retrieval logic
    if player_name.lower() == "tiger" and tournament_id.lower() == "masters":
        return {
            "name": "Tiger Woods",
            "tournament_name": "The Masters",
            "pars": [3, 3, 5, 4, 3, 4, 5, 4, 4, 4, 3, 5, 3, 5, 4, 5, 3, 3],
            "scores": [4, 3, 5, 3, 4, 4, 5, 3, 4, 4, 3, 5, 3, 4, 4, 5, 3, 4]
        }
    return None

def get_top_10_players(tournament_id):
    # Replace with actual data retrieval logic
    return [
        {"rank": 1, "name": "Player 1", "score": "-10"},
        {"rank": 2, "name": "Player 2", "score": "-9"},
        {"rank": 3, "name": "Player 3", "score": "-8"},
        # ... up to top 10
    ]

@app.route(PUBLIC_API_PREFIX + '/slack/events', methods=['POST'])
@verify_slack_signature
#@validate_token
def post_slack_events(user_email=None):
    data = request.get_json(force=True)
    print(f"Got post_slack_events request from user: {user_email}: {data}")
    if data is None:
        print(f"Empty post body for request: {request}")
        return 'Post body empty', 400

    if 'challenge' in data:
        return jsonify(data['challenge'])

    channel = None
    if 'event' in data:
        event = data['event']
        channel = event['channel']
        try:
            print(f"Slack event received: {event}")
            if event['type'] == 'message' and not 'bot_id' in event:
                event_txt = event['text']
                print(f"Slack message event sent from bot '{event['user']}' for channel '{channel}': '{event_txt}'")
                return handle_slack_event(data, channel, event_txt)
            if event['type'] == 'app_mention' and 'text' in event:
                text = event['text']
                print(f"Slack app_mention event sent from bot '{event['user']}' for channel '{channel}': '{text}'")
                handle_slack_command(text, channel)
                return "", 200
                #event_txt = event['text']
                #end_app_id = event_txt.find('>')
                #if end_app_id >= 0 and event_txt[0] == '<' and event_txt[1] == '@':
                #    event_txt = event_txt[(end_app_id + 1):].strip()
                #print(f"Slack app_mention event sent from bot '{event['user']}' for channel '{channel}': '{event_txt}'")
                #return handle_slack_event(data, channel, event_txt)
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

