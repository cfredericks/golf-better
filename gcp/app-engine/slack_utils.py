from functools import wraps
from flask import abort, jsonify, request
import hashlib
import hmac
import os
import time
import uuid
from PIL import Image
from slack_sdk import WebClient
from auth_utils import get_gsm_secret

# Slack configuration
if not os.getenv('NO_SLACK'):
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN") or get_gsm_secret('golfbetter-api-slackbot-token')
    SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET") or get_gsm_secret('golfbetter-api-slackbot-signing-secret')
    slack_client = WebClient(token=SLACK_BOT_TOKEN)

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

def save_and_upload_slack_image(image: Image, channel, image_path=f'/tmp/{uuid.uuid4()}.png', text="Here is the golf scorecard:"):
    image.save(image_path)
    return upload_slack_image(channel, image_path, text)

def upload_slack_image(channel, image_path, text="Here is the golf scorecard:"):
    if not os.getenv("DRY_RUN"):
        try:
            slack_client.files_upload_v2(
                channels=channel,
                file=image_path,
                title="Golf Scorecard",
                initial_comment=text
            )
            return "", 200
        except Exception as e:
            return f'Error uploading image: {e}'
    else:
        return f'image: "{image_path}", text: {text}'
