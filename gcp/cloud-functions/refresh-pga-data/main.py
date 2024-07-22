import functions_framework
import gzip
import base64
import os
import argparse
import json
import requests
from datetime import datetime as dt
from google.cloud.sql.connector import Connector #, IPTypes
import sqlalchemy
from google.cloud import secretmanager
import pg8000

DEFAULT_PROJECT_ID = 'stoked-depth-428423-j7'
DEFAULT_VERSION_ID = 'latest'

GRAPHQL_ENDPOINT = 'https://orchestrator.pgatour.com/graphql'
GRAPHQL_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.pgatour.com',
    'priority': 'u=1, i',
    'referer': 'https://www.pgatour.com/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'x-amz-user-agent': 'aws-amplify/3.0.7',
    'x-api-key': 'da2-gsrx5bibzbb4njvhl7t37wqyl4',
    'x-pgat-platform': 'web'
}

SCHEDULE_TYPE = 'schedule'
PLAYERS_TYPE = 'players'
LEADERBOARD_TYPE = 'leaderboard'
TOURNAMENTS_TYPE = 'tournaments'
TOURNAMENT_OVERVIEW_TYPE = 'tournament_overview'
WEATHER_TYPE = 'weather'
SHOT_DETAILS_TYPE = 'shot_details'
SCORECARD_TYPE = 'scorecard'
ALL_DATA_TYPES = [
    SCHEDULE_TYPE,
    PLAYERS_TYPE,
    LEADERBOARD_TYPE,
    TOURNAMENTS_TYPE,
    TOURNAMENT_OVERVIEW_TYPE,
    WEATHER_TYPE,
    SHOT_DETAILS_TYPE,
    SCORECARD_TYPE
]

def get_gsm_secret(secret_id, project_id=DEFAULT_PROJECT_ID, version_id=DEFAULT_VERSION_ID):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    payload = response.payload.data.decode('UTF-8')
    return payload

def get_db_connection():
    db_user = os.getenv('DB_USER', default='postgres')
    db_password = os.getenv('DB_PASSWORD', default=get_gsm_secret('golf-better-cloudsql-password'))
    db_name = os.getenv('DB_NAME', default='postgres')
    db_instance_conn_name = os.getenv('INSTANCE_CONNECTION_NAME', default='stoked-depth-428423-j7:us-central1:golf-better')
    db_host = os.getenv('DB_HOST', default=f'/cloudsql/{db_instance_conn_name}')
    db_port = os.getenv('DB_PORT', default=5432)

    pw_log = "****" if db_password is not None else "<unset>"
    print(f'Connecting to PG on user={db_user}, pw={pw_log}, host={db_host}, port={db_port}, db={db_name}')

    connector = Connector()
    def getconn():
        if db_instance_conn_name:
            return connector.connect(
                db_instance_conn_name,
                "pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
                #ip_type=IPTypes.PRIVATE
            )
        else:
            return pg8000.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        connect_args={
            "port": db_port
        }
    )

    return pool

@functions_framework.http
def refresh_data(request):
    data_types = ALL_DATA_TYPES
    tournament_ids = None
    player_ids = None
    rounds = None
    dry_run = False
    if request is not None:
        request_json = request.get_json(silent=True, force=True)
        if request_json is not None:
            if 'dataTypes' in request_json:
                data_types = request_json.get('dataTypes')
            if 'tournamentIds' in request_json:
                tournament_ids = request_json.get('tournamentIds')
            if 'playerIds' in request_json:
                player_ids = request_json.get('playerIds')
            if 'rounds' in request_json:
                rounds = request_json.get('rounds')
            if 'dryRun' in request_json:
                dry_run = str(request_json.get('dryRun')).lower() == 'true'

    print(f"Refreshing PGA data for {tournament_ids if tournament_ids else 'current (if any) or previous tournament'} for data types: {data_types}...")

    last_updated = dt.utcnow()

    # Load tournament ID if needed
    schedule_data = None
    if not tournament_ids:
        print('Querying tournament schedule to find current (or previous) tournament IDs...')
        schedule_data = query_schedule()

        # Check for current tournament
        if 'upcoming' in schedule_data and len(schedule_data['upcoming']) > 0:
            current_tourn = [t for t in schedule_data['upcoming'][0]['tournaments'] if last_updated >= dt.fromtimestamp(t['startDate'] / 1000.0)]
            if len(current_tourn) > 0:
                tournament_ids = [c['id'] for c in current_tourn]
                print(f"Using current tournament(s): {tournament_ids}")

        # Use previous tournament
        if not tournament_ids and 'completed' in schedule_data and len(schedule_data['completed']) > 0:
            prev_tourn = schedule_data['completed'][-1]['tournaments'][-1]
            if prev_tourn is not None:
                tournament_ids = [prev_tourn['id']]
                print(f"Using previous tournament(s): {tournament_ids}")

    if not tournament_ids:
        print('No current/previous tournament(s) found. Please specify --tournament-id')
        exit(0)

    if not dry_run:
        pool = get_db_connection()

    if SCHEDULE_TYPE in data_types:
        db_table = 'pga_tournaments'
        db_cols = ['id', 'name', 'start_date', 'is_completed', 'last_updated', 'data']
        if not schedule_data:
            schedule_data = query_schedule()

        print(f"Got {SCHEDULE_TYPE} response:")
        if dry_run:
            print(json.dumps(schedule_data))
        else:
            to_upsert = []
            for t_group in schedule_data.get('completed', []):
                for t in t_group.get('tournaments', []):
                    start_date = None
                    if 'startDate' in t:
                        start_date = dt.fromtimestamp(t['startDate'] / 1000.0).date()
                    to_upsert.append((
                        "'" + t["id"] + "'",
                        "'" + t["tournamentName"].replace("'", "''") + "'",
                        "'" + str(start_date) + "'" if start_date is not None else None,
                        True,
                        "'" + str(last_updated) + "'",
                        "'" + json.dumps(t).replace("'", "''") + "'"
                        ))
            for t_group in schedule_data.get('upcoming', []):
                for t in t_group.get('tournaments', []):
                    start_date = None
                    if 'startDate' in t:
                        start_date = dt.fromtimestamp(t['startDate'] / 1000.0).date()
                    to_upsert.append((
                        "'" + t["id"] + "'",
                        "'" + t["tournamentName"].replace("'", "''") + "'",
                        "'" + str(start_date) + "'" if start_date is not None else None,
                        False,
                        "'" + str(last_updated) + "'",
                        "'" + json.dumps(t).replace("'", "''") + "'"
                        ))
            msg, code = upsert(to_upsert, pool, db_table, db_cols)
            if code < 200 or code >= 300:
                return msg, code

    if PLAYERS_TYPE in data_types:
        data = query_players()
        db_table = 'pga_players'
        db_cols = ['id', 'name', 'last_updated', 'data']
        to_upsert = []
        for p in data:
            to_upsert.append((
                "'" + p['id'] + "'",
                "'" + p['displayName'].replace("'", "''") + "'",
                "'" + str(last_updated) + "'",
                "'" + json.dumps(p).replace("'", "''") + "'"
            ))
        msg, code = upsert(to_upsert, pool, db_table, db_cols)
        if code < 200 or code >= 300:
            return msg, code


    # TODO: Parallelize all nested loops for tournament ID, player ID, and round
    for tournament_id in tournament_ids:
        # If requires rounds, load if needed
        leaderboard_data = None
        rounds_to_query = rounds
        player_ids_to_query = player_ids
        if SHOT_DETAILS_TYPE in data_types and not rounds_to_query:
            print(f'Querying leaderboard for {tournament_id} to find player IDs or rounds...')
            leaderboard_data = query_leaderboard_v3(tournament_id)
            current_round_str = leaderboard_data['leaderboardRoundHeader']
            if current_round_str is not None and len(current_round_str) == 2 and current_round_str[0] == 'R':
                current_round = int(current_round_str[1])
                if current_round < 1 and current_round > 9:
                    print(f'Unable to parse current round from leaderboard for {tournament_id}, so using 1-4')
                    current_round = 4
                rounds_to_query = list(range(1, current_round + 1))
            if not rounds_to_query:
                print(f'Unable to load current round from leaderboard for {tournament_id}, so using 1-4')
                rounds_to_query = [1, 2, 3, 4]
            print(f'Using rounds: {rounds_to_query}')
        # If requires player IDs, load if needed
        if (SHOT_DETAILS_TYPE in data_types or SCORECARD_TYPE in data_types) and not player_ids_to_query:
            if not leaderboard_data:
                print(f'Querying leaderboard for {tournament_id} to find player IDs...')
                leaderboard_data = query_leaderboard_v3(tournament_id)
            # Filter out projected cut and actual cut line "players'
            player_ids_to_query = [p['id'] for p in leaderboard_data['players'] if '-' not in p['id']]
            print(f'Using player IDs: {player_ids_to_query}')

        for data_type in data_types:
            if data_type == SCHEDULE_TYPE or data_type == PLAYERS_TYPE:
                # Already handled outside loop
                continue

            db_tables = []
            db_cols = []
            to_upserts = []
            data = None
            if data_type == LEADERBOARD_TYPE:
                if not leaderboard_data:
                    leaderboard_data = query_leaderboard_v3(tournament_id)
                data = leaderboard_data
                db_tables.append('pga_leaderboard_players')
                db_cols.append(['id', 'tournament_id', 'player_id', 'last_updated', 'data'])
                to_upsert = []
                for p in leaderboard_data['players']:
                    if '-' not in p['id']:
                        to_upsert.append((
                            "'" + tournament_id + '-' + p['id'] + "'",
                            "'" + tournament_id + "'",
                            "'" + p['id'] + "'",
                            "'" + str(last_updated) + "'",
                            "'" + json.dumps(p).replace("'", "''") + "'"
                        ))
                to_upserts.append(to_upsert)
            elif data_type == TOURNAMENTS_TYPE:
                db_tables.append('tournaments')
                data = query_tournaments([tournament_id])
            elif data_type == TOURNAMENT_OVERVIEW_TYPE:
                db_tables.append('pga_tournament_overviews')
                data = query_tournament_overview(tournament_id)
            elif data_type == WEATHER_TYPE:
                db_tables.append('pga_weather')
                data = query_weather(tournament_id)
            elif data_type == SHOT_DETAILS_TYPE:
                db_tables.append('pga_shot_details')
                data = []
                for round in rounds_to_query:
                    for player_id in player_ids_to_query:
                        data.append(query_shot_details_v3(tournament_id, player_id, round))
            elif data_type == SCORECARD_TYPE:
                db_tables.append('pga_player_scorecards')
                db_cols.append(['id', 'tournament_id', 'player_id', 'last_updated', 'data'])
                data = []
                to_upsert = []
                for player_id in player_ids_to_query:
                    scorecard = query_scorecard_v3(tournament_id, player_id)
                    data.append(scorecard)
                    to_upsert.append((
                        "'" + tournament_id + '-' + scorecard['player']['id'] + "'",
                        "'" + tournament_id + "'",
                        "'" + scorecard['player']['id'] + "'",
                        "'" + str(last_updated) + "'",
                        "'" + json.dumps(scorecard).replace("'", "''") + "'"
                    ))
                to_upserts.append(to_upsert)
            else:
                raise Exception(f"Unknown data type: {data_type}")

            print(f"Got {data_type} response for {tournament_id}:")
            if dry_run:
                print(json.dumps(data))
                continue

            for i in range(0, len(db_tables)):
                msg, code = upsert(to_upserts[i], pool, db_tables[i], db_cols[i])
                if code < 200 or code >= 300:
                    return msg, code

    return '', 200

def upsert(to_upsert, pool, db_table, db_cols):
    if to_upsert:
        with pool.connect() as db_conn:
            try:
                arg_fmt = '(' + ','.join(['{}' for _ in range(0, len(to_upsert[0]))]) + ')'
                args_str = ','.join([arg_fmt.format(*t) for t in to_upsert])
                conflict_updates = ','.join([f'{c} = EXCLUDED.{c}' for c in db_cols])
                db_conn.execute(sqlalchemy.text(f"INSERT INTO {db_table} ({','.join(db_cols)}) VALUES " \
                    + args_str \
                    + f' ON CONFLICT (id) DO UPDATE SET {conflict_updates}'))
                db_conn.commit()
                print(f'Finished refreshing {db_table}')
            except Exception as e:
                print(f'Error writing to {db_table}: ', e)
                #raise e
                return '', 500

    return '', 200

def process_compressed(compressed_data):
    return json.loads(gzip.decompress(base64.b64decode(compressed_data)))

def query_schedule(year=dt.utcnow().year, tour_code='R'):
    data = {
        "operationName": "Schedule",
        "variables": {
            "tourCode": f"{tour_code}",
            "year": f"{year}"
        },
        "query": '''query Schedule($tourCode: String!, $year: String, $filter: TournamentCategory) {
            schedule(tourCode: $tourCode, year: $year, filter: $filter) {
                completed {
                    month
                    year
                    monthSort
                    ...ScheduleTournament
                }
                filters {
                    type
                    name
                }
                seasonYear
                tour
                upcoming {
                    month
                    year
                    monthSort
                    ...ScheduleTournament
                }
            }
        }
    
        fragment ScheduleTournament on ScheduleMonth {
            tournaments {
                tournamentName
                id
                beautyImage
                champion
                champions {
                    displayName
                    playerId
                }
                championEarnings
                championId
                city
                country
                countryCode
                courseName
                date
                dateAccessibilityText
                purse
                sortDate
                startDate
                state
                stateCode
                status {
                    roundDisplay
                    roundStatus
                    roundStatusColor
                    roundStatusDisplay
                }
                tournamentStatus
                ticketsURL
                tourStandingHeading
                tourStandingValue
                tournamentLogo
                display
                sequenceNumber
                tournamentCategoryInfo {
                    type
                    logoLight
                    logoDark
                    label
                }
                tournamentStatus
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return response.json()['data']['schedule']

def query_players(tour_code='R'):
    data = {
        "operationName": "PlayerDirectory",
        "variables": {
            "tourCode": f"{tour_code}"
        },
        "query": '''
        query PlayerDirectory($tourCode: TourCode!, $active: Boolean) {
            playerDirectory(tourCode: $tourCode, active: $active) {
                tourCode
                players {
                    id
                    isActive
                    firstName
                    lastName
                    shortName
                    displayName
                    alphaSort
                    country
                    countryFlag
                    headshot
                    playerBio {
                        id
                        age
                        education
                        turnedPro
                    }
                }
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return response.json()['data']['playerDirectory']['players']

def query_leaderboard_v3(tournament_id):
    data = {
        "operationName": "LeaderboardCompressedV3",
        "variables": {
            "leaderboardCompressedV3Id": f"{tournament_id}"
        },
        "query": '''query LeaderboardCompressedV3($leaderboardCompressedV3Id: ID!) {
            leaderboardCompressedV3(id: $leaderboardCompressedV3Id) {
                id
                payload
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return process_compressed(response.json()['data']['leaderboardCompressedV3']['payload'])

def query_tournaments(tournament_ids):
    data = {
        "operationName": "Tournaments",
        "variables": {
            "ids": tournament_ids
        },
        "query": '''query Tournaments($ids: [ID!]) {
            tournaments(ids: $ids) {
                id
                tournamentName
                tournamentLogo
                tournamentLocation
                tournamentStatus
                roundStatusDisplay
                roundDisplay
                roundStatus
                roundStatusColor
                currentRound
                timezone
                pdfUrl
                seasonYear
                displayDate
                country
                state
                city
                scoredLevel
                infoPath
                events {
                    id
                    eventName
                    leaderboardId
                }
                courses {
                    id
                    courseName
                    courseCode
                    hostCourse
                    scoringLevel
                }
                weather {
                    logo
                    logoDark
                    logoAccessibility
                    tempF
                    tempC
                    condition
                    windDirection
                    windSpeedMPH
                    windSpeedKPH
                    precipitation
                    humidity
                }
                ticketsURL
                tournamentSiteURL
                formatType
                features
                conductedByLabel
                conductedByLink
                beautyImage
                hideRolexClock
                hideSov
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return response.json()['data']['tournaments']

def query_tournament_overview(tournament_id):
    data = {
        "operationName": "TournamentOverview",
        "variables": {
            "tournamentId": f"{tournament_id}"
        },
        "query": '''query TournamentOverview($tournamentId: ID!) {
            tournamentOverview(tournamentId: $tournamentId) {
                beautyImage
                overview {
                    label
                    value
                    detail
                    secondaryDetail
                    wide
                    smallCopy
                }
                defendingChampion {
                    displaySeason
                    title
                    playerId
                    displayName
                    score
                    total
                    countryCode
                    seed
                    headshot
                }
                defendingTeamChampion {
                    displaySeason
                    title
                    playerId
                    displayName
                    score
                    total
                    countryCode
                    seed
                    headshot
                }
                pastChampions {
                    displaySeason
                    title
                    playerId
                    displayName
                    score
                    total
                    countryCode
                    seed
                    headshot
                }
                pastTeamChampions {
                    players {
                        displaySeason
                        title
                        playerId
                        displayName
                        score
                        total
                        countryCode
                        seed
                        headshot
                    }
                }
                ticketsURL
                webviewBrowserControls
                tourcastURL
                tourcastURLWeb
                shareURL
                eventGuideURL
                augmentedReality {
                    holes {
                        holeNumber
                    }
                }
                courses {
                    id
                    image
                    name
                    city
                    state
                    country
                    overview {
                        label
                        value
                        detail
                        secondaryDetail
                        wide
                        smallCopy
                    }
                }
                formatType
                activation {
                    title
                    sponsorLogo
                    sponsorLogoDark
                    data
                    description
                    detail
                }
                tournamentCategoryInfo {
                    type
                    logoLight
                    logoDark
                    label
                }
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return response.json()['data']['tournamentOverview']

def query_weather(tournament_id):
    data = {
        "operationName": "Weather",
        "variables": {
            "tournamentId": f"{tournament_id}"
        },
        "query": '''query Weather($tournamentId: ID!) {
            weather(tournamentId: $tournamentId) {
                title
                sponsorLogo
                accessibilityText
                hourly {
                    title
                    condition
                    windDirection
                    windSpeedKPH
                    windSpeedMPH
                    humidity
                    precipitation
                    temperature {
                        ... on StandardWeatherTemp {
                            __typename
                            tempC
                            tempF
                        }
                        ... on RangeWeatherTemp {
                            __typename
                            minTempC
                            minTempF
                            maxTempC
                            maxTempF
                        }
                    }
                }
                daily {
                    title
                    condition
                    windDirection
                    windSpeedKPH
                    windSpeedMPH
                    humidity
                    precipitation
                    temperature {
                        ... on StandardWeatherTemp {
                            __typename
                            tempC
                            tempF
                        }
                        ... on RangeWeatherTemp {
                            __typename
                            minTempC
                            minTempF
                            maxTempC
                            maxTempF
                        }
                    }
                }
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return response.json()['data']['weather']

def query_shot_details_v3(tournament_id, player_id, round):
    data = {
        "operationName": "ShotDetailsCompressedV3",
        "variables": {
            "tournamentId": f"{tournament_id}",
            "playerId": f"{player_id}",
            "round": round
        },
        "query": '''query ShotDetailsCompressedV3($tournamentId: ID!, $playerId: ID!, $round: Int!) {
            shotDetailsCompressedV3(
                tournamentId: $tournamentId
                playerId: $playerId
                round: $round
            ) {
                id
                payload
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    return process_compressed(response.json()['data']['shotDetailsCompressedV3']['payload'])

def query_scorecard_v3(tournament_id, player_id):
    data = {
        "operationName": "ScorecardCompressedV3",
        "variables": {
            "tournamentId": f"{tournament_id}",
            "playerId": f"{player_id}"
        },
        "query": '''query ScorecardCompressedV3($tournamentId: ID!, $playerId: ID!) {
            scorecardCompressedV3(tournamentId: $tournamentId, playerId: $playerId) {
                id
                payload
            }
        }'''
    }

    response = requests.post(GRAPHQL_ENDPOINT, headers=GRAPHQL_HEADERS, json=data)
    try:
        return process_compressed(response.json()['data']['scorecardCompressedV3']['payload'])
    except Exception as e:
        print(f'Error when parsing scorecard response for tid={tournament_id}, pid={player_id}: {response.json()}', e)
        raise e

# For running locally
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query PGA Tour APIs')
    parser.add_argument("-t",
                        "--data-types",
                        help="Data types to query",
                        nargs='+')
    parser.add_argument("-i",
                        "--tournament-ids",
                        help="Tournament IDs to query",
                        nargs='+')
    parser.add_argument("-p",
                        "--player-ids",
                        help="Player IDs to query (only relevant for shot_details and scorecard)",
                        nargs='+')
    parser.add_argument("-r",
                        "--rounds",
                        help="Rounds to query (only relevant for shot_details)",
                        nargs='+')
    parser.add_argument("-w",
                        "--write",
                        help="Whether to write results to DB or only print results",
                        action=argparse.BooleanOptionalAction,
                        default=False)
    args = parser.parse_args()

    post_body_json = {
        'dryRun': not args.write
    }
    if args.data_types:
        missing_data_types = [dt for dt in args.data_types if dt not in ALL_DATA_TYPES]
        if missing_data_types:
            print(f'Unknown data types specified: {missing_data_types}. Known datatypes are: {ALL_DATA_TYPES}')
            exit(1)
        post_body_json['dataTypes'] = args.data_types
    if args.tournament_ids:
        post_body_json['tournamentIds'] = args.tournament_ids
    if args.player_ids:
        post_body_json['playerIds'] = args.player_ids
    if args.rounds:
        post_body_json['rounds'] = args.rounds

    request = lambda: None
    request.get_json = lambda force, silent: post_body_json
    refresh_data(request)
