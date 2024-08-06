import json
import pytest

from ..auth_utils import get_gsm_secret, validate_token, DEFAULT_PROJECT_ID, DEFAULT_VERSION_ID
from flask import Flask, request

SECRET_PAYLOAD = b'secret-value'


@pytest.fixture
def mock_secret_manager(mocker):
    mock_client = mocker.patch('common.auth_utils.secretmanager.SecretManagerServiceClient')
    mock_instance = mock_client.return_value
    mock_response = mocker.Mock()
    mock_response.payload.data.decode.return_value = SECRET_PAYLOAD
    mock_instance.access_secret_version.return_value = mock_response
    return mock_instance

@validate_token
def dummy_function(user_email):
    return user_email

def test_get_gsm_secret_defaults(mock_secret_manager):
    secret_id = 'test-secret'
    secret = get_gsm_secret(secret_id)
    mock_secret_manager.access_secret_version.assert_called_once_with(name=f"projects/{DEFAULT_PROJECT_ID}/secrets/{secret_id}/versions/{DEFAULT_VERSION_ID}")
    assert secret == SECRET_PAYLOAD

def test_get_gsm_secret_overrides(mock_secret_manager):
    secret_id = 'test-secret'
    project_id = 'test-project-id'
    version_id = 'test-version-id'
    secret = get_gsm_secret(secret_id, project_id, version_id)
    mock_secret_manager.access_secret_version.assert_called_once_with(name=f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}")
    assert secret == SECRET_PAYLOAD

def test_validate_token(mocker):
    app = Flask(__name__)

    with app.test_request_context(headers={'Authorization': 'Bearer fake_token'}):
        # Mock the verify_id_token method
        mock_verify_id_token = mocker.patch('firebase_admin.auth.verify_id_token')
        mock_verify_id_token.return_value = {'email': 'test@example.com'}

        # Call the dummy function
        response = dummy_function()

        assert response == "test@example.com"

def test_validate_token_no_token(mocker):
    app = Flask(__name__)

    with app.test_request_context():
        # Call the dummy function
        response = dummy_function()

        assert json.loads(response[0]) == {"error": "Unauthorized"}
        assert response[1] == 401

def test_validate_token_invalid_token(mocker):
    app = Flask(__name__)

    with app.test_request_context(headers={'Authorization': 'Bearer fake_token'}):
        # Mock the verify_id_token method to raise an exception
        mock_verify_id_token = mocker.patch('firebase_admin.auth.verify_id_token')
        mock_verify_id_token.side_effect = Exception("Invalid token")

        # Call the dummy function
        response = dummy_function()

        assert json.loads(response[0]) == {"error": "Unauthorized"}
        assert response[1] == 401
