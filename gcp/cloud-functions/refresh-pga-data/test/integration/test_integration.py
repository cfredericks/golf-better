import main
import sqlalchemy
import time

from datetime import datetime, date, timezone

# TODO: Test other methods

def date_to_epoch_ms(d):
    dt = datetime.combine(d, datetime.min.time())
    epoch_time_seconds = time.mktime(dt.timetuple())
    return int(epoch_time_seconds * 1000)

def test_refresh_schedule(mocker):
    start_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    req = mocker.MagicMock()
    req.get_json = mocker.MagicMock(return_value={
        'dryRun': False,
        'allTournaments': False,
        'dataTypes': [main.SCHEDULE_TYPE],
        'tournamentIds': ['abc']
    })
    mock_query_schedule = mocker.patch('main.query_schedule')
    mock_query_schedule.return_value = {
        'upcoming': [
            {
                'tournaments': [
                    {'id': 'upcoming1', 'tournamentName': 'Upcoming1', 'startDate': date_to_epoch_ms(date(2024, 1, 1))},
                    {'id': 'upcoming2', 'tournamentName': 'Upcoming2', 'startDate': date_to_epoch_ms(date(2024, 1, 2))},
                ]
            },
            {
                'tournaments': [
                    {'id': 'upcoming3', 'tournamentName': 'Upcoming3', 'startDate': date_to_epoch_ms(date(2024, 1, 3))},
                    {'id': 'upcoming4', 'tournamentName': 'Upcoming4', 'startDate': date_to_epoch_ms(date(2024, 1, 4))},
                ]
            }
        ],
        'completed': [
            {
                'tournaments': [
                    {'id': 'completed1', 'tournamentName': 'Completed1', 'startDate': date_to_epoch_ms(date(2024, 2, 1))},
                    {'id': 'completed2', 'tournamentName': 'Completed2', 'startDate': date_to_epoch_ms(date(2024, 2, 2))},
                ]
            },
            {
                'tournaments': [
                    {'id': 'completed3', 'tournamentName': 'Completed3', 'startDate': date_to_epoch_ms(date(2024, 2, 3))},
                    {'id': 'completed4', 'tournamentName': 'Completed4', 'startDate': date_to_epoch_ms(date(2024, 2, 4))},
                ]
            }
        ]
    }

    # Clear table to start
    pool = main.get_db_connection()
    with pool.connect() as db_conn:
        db_conn.execute(sqlalchemy.text('delete from golfbetter.pga_tournaments'))
        db_conn.commit()

    # Refresh data
    err_msg, status_code = main.refresh_data(req)
    assert err_msg == ''
    assert status_code == 200

    # Validate results
    expected = [(
            t['id'],
            t['tournamentName'],
            datetime.fromtimestamp(t['startDate'] / 1000.0).date(),
            False,
            t)
        for group in mock_query_schedule.return_value['upcoming'] for t in group['tournaments']]
    expected.extend([(
        t['id'],
        t['tournamentName'],
        datetime.fromtimestamp(t['startDate'] / 1000.0).date(),
        True,
        t)
        for group in mock_query_schedule.return_value['completed'] for t in group['tournaments']])
    expected.sort(key=lambda obj: obj[0])

    with pool.connect() as db_conn:
        records = db_conn.execute(sqlalchemy.text('select id, name, start_date, is_completed, last_updated, data from golfbetter.pga_tournaments order by id')).fetchall()

        # Check last_updated
        for record in records:
            assert record[4] >= start_time

        db_data = [(row[0], row[1], row[2], row[3], row[5]) for row in records]
        assert db_data == expected