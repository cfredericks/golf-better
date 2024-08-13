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

To test the Slack integration without actually interacting with Slack, first run the app engine with Slack integration disabled:
```bash
NO_SLACK=1 python3 main.py
```

Then you can curl to the endpoint and it will print to console instead of responding to Slack, e.g.
```bash
curl -XPOST localhost:8080/api/v1/slack/events --data "{\"event_id\": \"$(uuidgen)\", \"event\": {\"channel\": \"test-channel\", \"user\": \"test-user\", \"type\": \"app_mention\", \"text\": \"@MyApp player info scheffler masters\"}}"
```

Or, as an example, generate an image and display it locally instead of sending to Slack:
```bash
open `curl -XPOST localhost:8080/api/v1/slack/events --data "{\"event_id\": \"$(uuidgen)\", \"event\": {\"channel\": \"test-channel\", \"user\": \"test-user\", \"type\": \"app_mention\", \"text\": \"@MyApp player info image greyser wyndh\"}}" | jq -r '.image'`
```

If you'd like to run a local app engine and have it actually interact with Slack, you can first run ngrok to port forward your app engine (need to register an account):
```bash
ngrok http 8080
```

Then you can update the Slack app "event subscription" settings at https://api.slack.com/apps to point to this new endpoint, e.g.
```bash
https://61e9-2601-642-4900-7-108a-a3e8-97f7-ce02.ngrok-free.app/api/v1/slack/events
```

Then when you run a local app engine, the Slack integration will be forwarded to your local instance.

# Endpoints

- `GET /api/v1/tournaments` - Tournaments
  - supports an optional `tournamentId` query param
- `GET /api/v1/players` - Players
  - supports an optional `playerId` query param
  - supports an optional `tournamentId` query param
- `POST /protected/api/v1/updateTournaments` - Manually refresh tournaments in DB
  - is protected and requires auth
