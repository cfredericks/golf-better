import main
import json
import pytest

from unittest.mock import MagicMock


# Mock data for the API response
mock_records = [
    MagicMock(**{"__getitem__.side_effect": lambda x: {'id': 1, 'name': 'Tournament 1'}}),
    MagicMock(**{"__getitem__.side_effect": lambda x: {'id': 2, 'name': 'Tournament 2'}})
]

@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

def test_get_tournaments_no_args(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check that execute was called with the correct query
    expected_query = "SELECT data FROM golfbetter.pga_tournaments where 1=1"
    actual_query = mock_execute.call_args[0][0].text
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    # Check the response data
    expected_response = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response

def test_get_tournaments_with_id(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock request
    m = mocker.MagicMock()
    m.args = {'id': 77}
    mocker.patch("main.request", m)

    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check that execute was called with the correct query
    expected_query = f"SELECT data FROM golfbetter.pga_tournaments where 1=1 and id = '{m.args['id']}'"
    actual_query = mock_execute.call_args[0][0].text
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    # Check the response data
    expected_response = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response

def test_get_players_no_args(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-leaderboard-players',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check that execute was called with the correct query
    expected_query = "SELECT data FROM golfbetter.pga_leaderboard_players where 1=1"
    actual_query = mock_execute.call_args[0][0].text
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    # Check the response data
    expected_response = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response

def test_get_players_with_id(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock request
    m = mocker.MagicMock()
    m.args = {'id': 77, 'tournamentId': 88}
    mocker.patch("main.request", m)

    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-leaderboard-players',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check that execute was called with the correct query
    expected_query = f"SELECT data FROM golfbetter.pga_leaderboard_players where 1=1 and tournament_id = '{m.args['tournamentId']}' and id = '{m.args['id']}'"
    actual_query = mock_execute.call_args[0][0].text
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    # Check the response data
    expected_response = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response

def test_get_player_scorecards_no_args(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-player-scorecards',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check that execute was called with the correct query
    expected_query = "SELECT data FROM golfbetter.pga_player_scorecards where 1=1"
    actual_query = mock_execute.call_args[0][0].text
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    # Check the response data
    expected_response = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response

def test_get_player_scorecards_with_id(client, mocker):
    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Mock request
    m = mocker.MagicMock()
    m.args = {'id': 77, 'tournamentId': 88}
    mocker.patch("main.request", m)

    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-player-scorecards',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check that execute was called with the correct query
    expected_query = f"SELECT data FROM golfbetter.pga_player_scorecards where 1=1 and tournament_id = '{m.args['tournamentId']}' and id = '{m.args['id']}'"
    actual_query = mock_execute.call_args[0][0].text
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    # Check the response data
    expected_response = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response
