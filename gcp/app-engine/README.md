# Deploy

```bash
gcloud app deploy
```

You can then query the deployed app engine endpoints using something like:
```bash
curl https://stoked-depth-428423-j7.uc.r.appspot.com/{ENDPOINT}
```
e.g.
```bash
curl https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/tournaments
```

# Run locally

```bash
pip3 install -r requirements.txt
python3 main.py
```

You can then query the locally flask app endpoints using something like:
```bash
curl http://127.0.0.1:8080/{ENDPOINT}
```
e.g.
```bash
curl http://127.0.0.1:8080/api/v1/tournaments
```

To test slack without actually integration with slack, first run the app engine with slack integration disabled:
```bash
NO_SLACK=1 python3 main.py
```

Then you can curl to the endpoint and it will print to console instead of responding to Slack, e.g.
```bash
curl -XPOST localhost:8080/api/v1/slack/events --data '{"event": {"channel": "test-channel", "user": "test-user", "type": "app_mention", "text": "@MyApp player info thomps wyndh"}}'
```

# Endpoints

- `GET /api/v1/tournaments` - Tournaments
  - supports an optional `tournamentId` query param
- `GET /api/v1/players` - Players
  - supports an optional `playerId` query param
  - supports an optional `tournamentId` query param
- `POST /protected/api/v1/updateTournaments` - Manually refresh tournaments in DB
  - is protected and requires auth
