from functools import wraps
from flask import request, g
import json
from google.cloud import secretmanager
from firebase_admin import auth

DEFAULT_PROJECT_ID = 'stoked-depth-428423-j7'
DEFAULT_VERSION_ID = 'latest'


def get_decoded_token():
    """Get decoded token from Authorization header."""
    if 'Authorization' not in request.headers:
        return None
    try:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        return auth.verify_id_token(id_token)
    except Exception as e:
        print("Exception decoding auth token", e)
        return None


def get_user_id_from_token():
    """Get user ID (uid) from the current request's auth token."""
    if hasattr(g, 'decoded_token') and g.decoded_token:
        return g.decoded_token.get('uid')
    decoded_token = get_decoded_token()
    if decoded_token:
        return decoded_token.get('uid')
    return None


# Decorator to parse auth token and extract user email
def validate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        decoded_token = get_decoded_token()

        if not decoded_token:
            return json.dumps({"error": "Unauthorized"}), 401

        # Store decoded token in flask g for later use
        g.decoded_token = decoded_token

        user_email = decoded_token.get('email')
        return f(user_email, *args, **kwargs)
    return decorated_function

def get_gsm_secret(secret_id, project_id=DEFAULT_PROJECT_ID, version_id=DEFAULT_VERSION_ID):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    payload = response.payload.data.decode('UTF-8')
    return payload
