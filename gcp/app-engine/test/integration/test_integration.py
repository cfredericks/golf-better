import main
import json
import pytest
import sqlalchemy

from common.data_model_factories import PGATournamentFactory
from common.schemas import TournamentSchema
from common.db import get_db_connection

# TODO: Test other methods

@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

def generate_tournament_data():
    data = [PGATournamentFactory(), PGATournamentFactory()]
    schema = TournamentSchema()

    # Write test data
    pool = get_db_connection()
    with pool.connect() as db_conn:
        db_conn.execute(sqlalchemy.text('delete from golfbetter.pga_tournaments'))
        for datum in data:
            db_conn.execute(sqlalchemy.text(f'''
                insert into golfbetter.pga_tournaments (id, name, start_date, is_completed, data, last_updated)
                values ('{datum.id}', '{datum.name.replace("'", "''")}', '{datum.start_date}', {str(datum.is_completed).lower()}, '{json.dumps(schema.dump(datum.data)).replace("'", "''")}', '{datum.last_updated}')
                '''))
        db_conn.commit()

    return data

def test_get_pga_tournaments_no_args(client, mocker):
    data = generate_tournament_data()

    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check the response data
    assert response.status_code == 200
    schema = TournamentSchema(many=True)
    expected_response = schema.dump([record.data for record in data])
    assert json.loads(response.data) == expected_response

def test_get_tournaments_with_id(client, mocker):
    data = generate_tournament_data()
    id_to_query = data[1].id

    # Mock request
    m = mocker.MagicMock()
    m.args = {'id': id_to_query}
    m.headers = {'Authorization': 'Bearer test_token'}
    mocker.patch("main.request", m)

    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check the response data
    assert response.status_code == 200
    schema = TournamentSchema(many=True)
    expected_response = schema.dump([record.data for record in data if record.id == id_to_query])
    assert json.loads(response.data) == expected_response

def test_get_tournaments_with_id_no_match(client, mocker):
    generate_tournament_data()
    id_to_query = 'unknown-id'

    # Mock request
    m = mocker.MagicMock()
    m.args = {'id': id_to_query}
    m.headers = {'Authorization': 'Bearer test_token'}
    mocker.patch("main.request", m)

    # Mock firebase auth
    mock_decoded_token = {'email': 'test@example.com'}
    mocker.patch('firebase_admin.auth.verify_id_token', return_value=mock_decoded_token)

    # Make the request to the API
    response = client.get(
        '/api/v1/pga-tournaments',
        headers={'Authorization': 'Bearer test_token'}
    )

    # Check the response data
    assert response.status_code == 200
    assert json.loads(response.data) == []
