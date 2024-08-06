import main
import json
import pytest

from common.data_model_factories import PGATournamentFactory, PGALeaderboardPlayerFactory, PGAPlayerScorecardFactory
from common.schemas import TournamentSchema, PlayerRowV3Schema, ScorecardV3Schema


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

def test_get_pga_tournaments_success(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_tournaments')
    mock_method.return_value = [PGATournamentFactory(), PGATournamentFactory()]

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check the response data
    assert response.status_code == 200
    schema = TournamentSchema(many=True)
    expected_response = schema.dump([record.data for record in mock_method.return_value])
    assert json.loads(response.data) == expected_response

def test_get_pga_tournaments_fail(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_tournaments')
    mock_method.side_effect = Exception("test exception")

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    assert response.status_code == 500

def test_get_pga_tournaments_fail_noauth(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_tournaments')
    mock_method.return_value = []

    # Make the request to the API
    response = client.get('/api/v1/pga-tournaments')

    assert response.status_code == 401

def test_get_pga_leaderboard_players_success(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_leaderboard_players')
    mock_method.return_value = [PGALeaderboardPlayerFactory(), PGALeaderboardPlayerFactory()]

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-leaderboard-players',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check the response data
    assert response.status_code == 200
    schema = PlayerRowV3Schema(many=True)
    expected_response = schema.dump([record.data for record in mock_method.return_value])
    assert json.loads(response.data) == expected_response

def test_get_pga_leaderboard_players_fail(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_leaderboard_players')
    mock_method.side_effect = Exception("test exception")

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-leaderboard-players',
        headers={'Authorization': 'Bearer test_token'}
    )

    assert response.status_code == 500

def test_get_pga_leaderboard_players_fail_noauth(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_leaderboard_players')
    mock_method.return_value = []

    # Make the request to the API
    response = client.get('/api/v1/pga-leaderboard-players')

    assert response.status_code == 401

def test_get_pga_player_scorecards_success(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_player_scorecards')
    mock_method.return_value = [PGAPlayerScorecardFactory(), PGAPlayerScorecardFactory()]

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-player-scorecards',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check the response data
    assert response.status_code == 200
    schema = ScorecardV3Schema(many=True)
    expected_response = schema.dump([record.data for record in mock_method.return_value])
    assert json.loads(response.data) == expected_response

def test_get_pga_player_scorecards_fail(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_player_scorecards')
    mock_method.side_effect = Exception("test exception")

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-player-scorecards',
        headers={'Authorization': 'Bearer test_token'}
    )

    assert response.status_code == 500

def test_get_pga_player_scorecards_fail_noauth(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.get_player_scorecards')
    mock_method.return_value = []

    # Make the request to the API
    response = client.get('/api/v1/pga-player-scorecards')

    assert response.status_code == 401

def test_post_user_success(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.upsert_user')
    mock_method.return_value = [PGAPlayerScorecardFactory(), PGAPlayerScorecardFactory()]

    # Make the request to the API
    response = client.post(
        '/api/v1/users',
        headers={'Authorization': 'Bearer test_token'},
        data='{"email": "foo"}'
    )

    assert response.status_code == 201

def test_post_user_fail(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.upsert_user')
    mock_method.side_effect = Exception("test exception")

    # Make the request to the API
    response = client.post(
        '/api/v1/users',
        headers={'Authorization': 'Bearer test_token'},
        data='{"email": "foo"}'
    )

    assert response.status_code == 500

def test_post_user_fail_no_body(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.upsert_user')
    mock_method.side_effect = Exception("test exception")

    # Make the request to the API
    response = client.post(
        '/api/v1/users',
        headers={'Authorization': 'Bearer test_token'},
        data=None
    )

    assert response.status_code == 400

def test_post_user_fail_no_email(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.upsert_user')
    mock_method.side_effect = Exception("test exception")

    # Make the request to the API
    response = client.post(
        '/api/v1/users',
        headers={'Authorization': 'Bearer test_token'},
        data='{"id": "foo"}'
    )

    assert response.status_code == 400

def test_post_user_noauth(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock data
    mock_method = mocker.patch('main.upsert_user')
    mock_method.return_value = []

    # Make the request to the API
    response = client.post('/api/v1/users', data='')

    assert response.status_code == 401
