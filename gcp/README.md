# Setup infra

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
```

# Connecting to cloud sql locally

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