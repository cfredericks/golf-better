import json

from ..data_model_factories import PGATournamentFactory, PGALeaderboardPlayerFactory, PGAPlayerScorecardFactory
from ..schemas import TournamentSchema, PlayerRowV3Schema, ScorecardV3Schema

def test_get_pga_tournaments_no_args(client, mocker):
    data = [PGATournamentFactory(), PGATournamentFactory()]
    mock_db_connection = mocker.patch('common.db.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = data

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

def test_get_pga_tournaments_with_id(client, mocker):
    mock_db_connection = mocker.patch('common.db.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get('/api/v1/pga-tournaments')

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

def test_get_pga_leaderboard_players_no_args(client, mocker):
    data = []
    mock_db_connection = mocker.patch('common.db.get_db_connection')
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

def test_get_pga_leaderboard_players_with_id(client, mocker):
    mock_db_connection = mocker.patch('common.db.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get('/api/v1/pga-leaderboard-players')

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

def test_get_pga_player_scorecards_no_args(client, mocker):
    mock_db_connection = mocker.patch('common.db.get_db_connection')
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

def test_get_pga_player_scorecards_with_id(client, mocker):
    mock_db_connection = mocker.patch('common.db.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute
    mock_execute.return_value.fetchall.return_value = mock_records

    # Make the request to the API
    response = client.get('/api/v1/pga-player-scorecards')

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
