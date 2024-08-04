import main
import json
import pytest
import sqlalchemy

from datetime import date, datetime

@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

def test_get_tournaments_no_args(client, mocker):
    data = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]

    # Write test data
    pool = main.get_db_connection()
    with pool.connect() as db_conn:
        now = datetime.utcnow()
        db_conn.execute(sqlalchemy.text('delete from golfbetter.pga_tournaments'))
        for datum in data:
            db_conn.execute(sqlalchemy.text(f'''
                insert into golfbetter.pga_tournaments (id, name, start_date, is_completed, data, last_updated)
                values ('{datum['id']}', '{datum['name']}', '{str(now.date())}', false, '{json.dumps(datum)}', '{str(now)}')
                '''))
        db_conn.commit()

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
    assert json.loads(response.data) == data

def test_get_tournaments_with_id(client, mocker):
    id_to_query = 2
    data = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': id_to_query, 'name': 'Tournament 2'}
    ]

    # Write test data
    pool = main.get_db_connection()
    with pool.connect() as db_conn:
        now = datetime.utcnow()
        db_conn.execute(sqlalchemy.text('delete from golfbetter.pga_tournaments'))
        for datum in data:
            db_conn.execute(sqlalchemy.text(f'''
                insert into golfbetter.pga_tournaments (id, name, start_date, is_completed, data, last_updated)
                values ('{datum['id']}', '{datum['name']}', '{str(now.date())}', false, '{json.dumps(datum)}', '{str(now)}')
                '''))
        db_conn.commit()

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
    assert json.loads(response.data) == [datum for datum in data if datum['id'] == id_to_query]

def test_get_tournaments_with_id_no_match(client, mocker):
    id_to_query = 3
    data = [
        {'id': 1, 'name': 'Tournament 1'},
        {'id': 2, 'name': 'Tournament 2'}
    ]

    # Write test data
    pool = main.get_db_connection()
    with pool.connect() as db_conn:
        now = datetime.utcnow()
        db_conn.execute(sqlalchemy.text('delete from golfbetter.pga_tournaments'))
        for datum in data:
            db_conn.execute(sqlalchemy.text(f'''
                insert into golfbetter.pga_tournaments (id, name, start_date, is_completed, data, last_updated)
                values ('{datum['id']}', '{datum['name']}', '{str(now.date())}', false, '{json.dumps(datum)}', '{str(now)}')
                '''))
        db_conn.commit()

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
