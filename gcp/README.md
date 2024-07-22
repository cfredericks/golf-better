# Cloud resources

- Cloud SQL: https://console.cloud.google.com/sql/instances/golf-better/overview?project=stoked-depth-428423-j7
- Cloud functions: https://console.cloud.google.com/functions/list?project=stoked-depth-428423-j7
- CRON schedules: https://console.cloud.google.com/cloudscheduler?project=stoked-depth-428423-j7
- App Engine: https://console.cloud.google.com/appengine?serviceId=default&project=stoked-depth-428423-j7


# Infra commands

```bash
# Setup VPC connector
gcloud compute networks vpc-access connectors create my-connector \
    --region us-central1 \
    --network default \
    --range 10.8.0.0/28
```

# DB Schemas

```sql
-- Tables
create table tournaments (id int primary key, name text not null, start_date date, end_date date, data jsonb not null, last_updated timestamp with time zone not null);
create table tournament_players (id int primary key, player_id int not null, tournament_id int not null, name text not null, last_updated timestamp with time zone not null, data jsonb not null);

-- Indexes
create unique index tournaments_start_date_name on tournaments (start_date, name);
create unique index tournament_players_player_id_tournament_id on tournament_players (player_id, tournament_id);
create index tournament_players_tournament_id on tournament_players (tournament_id);

-- PGA Tables
create table pga_tournaments (id text primary key, name text not null, start_date date, is_completed boolean not null, data jsonb not null, last_updated timestamp with time zone not null);
create table pga_leaderboard_players (id text primary key, tournament_id text not null, player_id text not null, data jsonb not null, last_updated timestamp with time zone not null);
create table pga_player_scorecards (id text primary key, tournament_id text not null, player_id text not null, data jsonb not null, last_updated timestamp with time zone not null);

-- PGA Indexes
create index pga_tournaments_start_date on pga_tournaments (start_date);
create index pga_tournaments_is_completed on pga_tournaments (is_completed);
create index pga_leaderboard_players_tournament_id on pga_leaderboard_players (tournament_id);
create index pga_leaderboard_players_player_id on pga_leaderboard_players (player_id);
create index pga_player_scorecardss_tournament_id on pga_player_scorecards (tournament_id);
create index pga_player_scorecardss_player_id on pga_player_scorecards (player_id);
```

# Connecting to cloud sql locally

Either use Cloud SQL Studio, i.e. https://console.cloud.google.com/sql/instances/golf-better/studio?authuser=1&project=stoked-depth-428423-j7

Or to connect from your local machine using port forwarding:

1. Enable public IP on the instance here: https://console.cloud.google.com/sql/instances/golf-better/overview?authuser=1&project=stoked-depth-428423-j7
2. Install proxy (if not already done)
```bash
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy
./cloud-sql-proxy stoked-depth-428423-j7:us-central1:golf-better --private-ip
```
3. Start proxy
```bash
./cloud-sql-proxy stoked-depth-428423-j7:us-central1:golf-better --private-ip
```
4. Run PSQL to connect to DB (in a separate tab)
```bash
PGPASSWORD='{DB_PASSWORD}' psql -h {PUBLIC_IP} -p 5432 -U postgres
```