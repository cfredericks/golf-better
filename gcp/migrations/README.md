To run migrations against a DB, run:
```bash
PGPASSWORD=password sqitch deploy db:pg://postgres@localhost:15432/postgres
```

Where the general pattern is
```bash
PGPASSWORD="$PASSWORD" sqitch deploy db:pg://"$DB_USER"@"$DB_HOST":"$DB_PORT"/"$DB_NAME"
```

To verify migrations against a DB, run:
```bash
PGPASSWORD=password sqitch verify db:pg://postgres@localhost:15432/postgres
```