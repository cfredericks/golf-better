from PIL import Image, ImageDraw, ImageFont
from db_queries import get_next_tournaments, get_player, get_top_players
import os
from slack_utils import save_and_upload_slack_image
if not os.getenv('NO_SLACK'):
    from slack_utils import slack_client
from utils import try_cast_to_int


def handle_slack_command(command_text, channel):
    command_text = command_text.lower()

    msg = ""
    status_code = 200
    # Handle tournament info command
    if "tournament info" in command_text:
        msg, status_code = handle_tournament_info(command_text)

    # Handle player info command
    elif "player info image" in command_text:
        msg, status_code = handle_player_info_image(command_text, channel)

    # Handle player info command
    elif "player info" in command_text:
        msg, status_code = handle_player_info(command_text)

    # Handle top 10 players command
    elif "top 10" in command_text:
        msg, status_code = handle_top_10_players(command_text)

    # Handle unknown command
    else:
        msg = "Sorry, I didn't understand that command. Please try 'tournament info', 'player info image', 'player info', or 'top 10'" + \
          " (NOTE: for these test endpoints, the only supported player is 'tiger', and the only supported tournament is 'masters'."
        status_code = 404

    print(f'Finished processing, code={status_code}, msg={msg}')
    if msg:
        if not os.getenv('NO_SLACK'):
            slack_client.chat_postMessage(channel=channel, text=msg)
        else:
            print(f'Would respond to slack event with channel={channel}, text={msg}')
    return msg, status_code

def handle_tournament_info(command_text):
    # Parse for specific tournament ID or name
    words = command_text.split()
    if len(words) > 3:
        tournament_id = words[-1]  # Assume the last word is the ID
        tournament = get_next_tournaments(tournament_id)
        if tournament:
            response_text = (
                f"*{tournament['name']}*:\n"
                f"Location: {tournament['location']}\n"
                f"Date: {tournament['date']}\n"
                f"Status: {tournament['status']}\n"
            )
            return response_text, 200
        else:
            return "Tournament not found.", 404

    # Next N tournaments
    tournaments = get_next_tournaments()
    response_text = "*Tournaments:*\n"
    for tournament in tournaments:
        response_text += f"- {tournament['name']} ({tournament['status']}) - {tournament['date']}\n"

    return response_text, 200

def handle_player_info(command_text):
    # Parse for specific player name/id and tournament name/id
    words = command_text.split()
    round = None
    if len(words) > 4:
        if len(words) > 5:
            player_search = words[-3]  # Assume third last word is player name/id
            tournament_search = words[-2]  # Assume second last word is the tournament name/id
            round = try_cast_to_int(words[-1], None)  # Assume the last word is the round
            if round is None or round < 1 or round > 4:
                return 'When calling "player info <player> <tournament> <round>", the round must be an integer between 1 and 4', 400
        else:
            player_search = words[-2]  # Assume second last word is player name/id
            tournament_search = words[-1]  # Assume the last word is the tournament name/id

        player_info = get_player(player_search, tournament_search, round)
        if player_info:
            response_text = f"*{player_info['name']}* in *{player_info['tournament_name']}* (Round {player_info['round']}):\n" + \
                f"Scores:\n{format_scores_grid(player_info['pars'], player_info['scores'])}"
            return response_text, 200
        else:
            return  "Player or tournament not found.", 404

    return "Please specify both a player and a tournament.", 400

def handle_player_info_image(command_text, channel):
    # Parse for specific player name/id and tournament name/id
    words = command_text.split()
    round = None
    if len(words) > 5:
        if len(words) > 6:
            player_search = words[-3]  # Assume third last word is player name/id
            tournament_search = words[-2]  # Assume second last word is the tournament name/id
            round = try_cast_to_int(words[-1], None)  # Assume the last word is the round
            if round is None or round < 1 or round > 4:
                return 'When calling "player info image <player> <tournament> <round>", the round must be an integer between 1 and 4', 400
        else:
            player_search = words[-2]  # Assume second last word is player name/id
            tournament_search = words[-1]  # Assume the last word is the tournament name/id

        player_info = get_player(player_search, tournament_search, round)
        if player_info:
            try:
                # Create and save the image
                text = f"*{player_info['name']}* in *{player_info['tournament_name']}* (Round {player_info['round']}):"
                image = create_golf_scorecard_image(player_info)
                return save_and_upload_slack_image(image, channel, text=text)
            except Exception as e:
                print('Error creating image', e)
                return f'Error creating image: {e}', 500

        return "Player or tournament not found.", 404

    return "Please specify both a player and a tournament.", 400

def handle_top_10_players(command_text):
    words = command_text.split()
    if len(words) > 3:
        tournament_search = words[-1]  # Assume the last word is the tournament name/id
        top_10_players = get_top_players(tournament_search, limit=10)
        if top_10_players:
            response_text = "*Top 10 Players:*\n"
            for player in top_10_players:
                response_text += (
                    f"{player['rank']}. {player['name']} - Score: {player['score']}\n"
                )
            return response_text, 200

        return "Tournament not found.", 404

    return "Please specify a tournament.", 400

def format_scores_grid(pars, scores):
    score_icons = []
    for i in range(len(pars)):
        score_int = try_cast_to_int(scores[i], pars[i])
        if score_int < pars[i]:
            score_icons.append("🟢")
        elif score_int > pars[i]:
            score_icons.append("🔴")
        else:
            score_icons.append("  ")
    grid = "```\n"
    grid += " Hole  |" + "|".join([" " + str(i).ljust(3) for i in range(1, 19)]) + "|\n"
    grid += "-------|" + "|".join(["----" for _ in range(1, 19)]) + "|\n"
    grid += " Par   |" + "|".join([" " + str(par).ljust(3) for par in pars]) + "|\n"
    grid += "-------|" + "|".join(["----" for _ in range(1, 19)]) + "|\n"
    grid += " Score |" + "|".join([" " + str(score).ljust(3) for score in scores]) + "|\n"
    grid += "       | " + " | ".join([icon for icon in score_icons]) + " |\n```"
    return grid

# "player_info" is of the format:
# {
#   "name": "player name",
#   "tournament_name": "tournament name",
#   "round": 1-4,
#   "pars": [parHole1, parHole2,...],
#   "scores": [scoreHole1, scoreHole2,...]
# }
def create_golf_scorecard_image(player_info):
    # Image dimensions
    width = 800
    height = 80  # Adjust the height to fit the additional row for par values
    cell_width = width // 18

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
    for i in range(len(player_info['pars'])):
        x0 = i * cell_width
        y0 = 0
        x1 = x0 + cell_width

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
        par_text = f"Par {player_info['pars'][i]}"
        text_bbox = draw.textbbox((0, 0), par_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x0 + cell_width / 2 - text_width / 2
        text_y = y0 + 25 - text_height / 2  # Positioned below the hole number
        draw.text((text_x, text_y), par_text, fill=black, font=font)

        # Draw the horizontal grid line underneath the par value text
        draw.line([(x0, text_y + text_height + 5), (x1, text_y + text_height + 5)], fill=black, width=2)

        # Calculate the result based on par and shots
        score = player_info['scores'][i]
        par = player_info['pars'][i]

        # Calculate the text size
        text_bbox = draw.textbbox((0, 0), score, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate centered position
        shape_center_x = x0 + cell_width / 2
        shape_center_y = y0 + 55  # Adjust the center of the grid square for scores
        text_x = shape_center_x - text_width / 2
        text_y = shape_center_y - text_height / 2

        shots = try_cast_to_int(score, par)
        if shots < par:  # Birdie or better
            for i in range(0, par-shots):
                draw.ellipse([shape_center_x - 10 + i*2, shape_center_y - 10 + i*2, shape_center_x + 10 - i*2, shape_center_y + 10 - i*2], outline=green, width=1)
            draw.text((text_x, text_y), score, fill=black, font=font)

        elif shots > par:  # Bogey or worse
            for i in range(0, shots-par):
                draw.rectangle([shape_center_x - 10 + i*2, shape_center_y - 10 + i*2, shape_center_x + 10 - i*2, shape_center_y + 10 - i*2], outline=blue, width=1)
            draw.text((text_x, text_y), score, fill=black, font=font)

        else:  # Par
            draw.text((text_x, text_y), score, fill=black, font=font)

    # Draw the final horizontal line at the bottom
    draw.line([(0, height), (width, height)], fill=black, width=2)

    return image
