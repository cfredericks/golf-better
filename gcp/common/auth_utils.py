"""
Helpers for managing auth in a Flask API.
"""

import firebase_admin
import json
from firebase_admin import auth
from flask import request
from functools import wraps
from google.cloud import secretmanager


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