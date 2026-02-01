# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Golf-Better is a full-stack application for tracking PGA Tour golfers, tournaments, and fantasy golf leagues:
- **Web App** (`/web`) - React SPA on Firebase Hosting for viewing leaderboards and managing fantasy leagues
- **App Engine** (`/gcp/app-engine`) - Flask API serving data to web app and Slack bot
- **Cloud Functions** (`/gcp/cloud-functions/`) - Periodic sync of PGA Tour data into CloudSQL
- **Database migrations** (`/gcp/migrations`) - Sqitch-managed PostgreSQL schema

## Docker-Based Development

All commands run through Docker containers. Use `make help` to see available commands.

### Quick Start
```bash
# Start all services (postgres, backend, web)
make up

# View logs
make logs

# Stop all services
make down
```

### Common Commands
```bash
# Run all tests
make test

# Run all linters
make lint

# Run database migrations
make migrate

# Build web app for production
make build-web

# Open PostgreSQL shell
make db-shell
```

### Individual Service Commands
```bash
# Backend only
make test-api      # Run backend tests
make lint-api      # Run ruff linter
make logs-api      # View backend logs

# Web only
make test-web      # Run web tests
make lint-web      # Run eslint
make logs-web      # View web logs
```

### Manual Docker Commands
```bash
# Run a command in the backend container
docker compose run --rm backend pytest test/test_fantasy_scoring.py -v

# Run a command in the web container
docker compose run --rm web npm run build

# Access running container
docker compose exec backend bash
docker compose exec web sh
```

## Architecture

```
React Web App (Firebase Auth)
    ↓ HTTPS
App Engine (Flask + CORS)
    ↓ SQLAlchemy
Cloud SQL (PostgreSQL, schema: golfbetter)
    ↑
Cloud Functions (periodic PGA data sync via Cloud Scheduler)
```

**Key data flow:**
1. Cloud Functions fetch from PGA Tour GraphQL API → store in PostgreSQL
2. App Engine serves data to web app (requires Firebase JWT)
3. Slack bot receives mentions → queries DB → responds in channel

## Database Schema

All tables in `golfbetter` schema:

**PGA Data (JSONB data columns):**
- `pga_tournaments` - Tournament info (indexed by start_date, is_completed)
- `pga_players` - Player info
- `pga_leaderboard_players` - Tournament standings
- `pga_player_scorecards` - Round-by-round scores

**User & App Data:**
- `users` - App users (email unique)
- `player_groups` - User-created player groupings

**Fantasy Leagues:**
- `leagues` - Fantasy league configurations
- `league_members` - League membership
- `tournament_picks` - User picks per tournament
- `fantasy_scores` - Calculated scores (cached)
- `user_favorites` - Favorite players/tournaments
- `league_invitations` - Pending invites

## API Endpoints

### PGA Data
- `GET /api/v1/pga-tournaments` - List tournaments (optional `id` param)
- `GET /api/v1/pga-leaderboard-players` - Leaderboard (optional `tournamentId`, `id` params)
- `GET /api/v1/pga-player-scorecards` - Scorecards (optional `tournamentId`, `id` params)

### Fantasy Leagues
- `GET/POST /api/v1/leagues` - List/create leagues
- `GET/PUT /api/v1/leagues/<id>` - League details/update
- `GET /api/v1/leagues/<id>/members` - League members
- `POST /api/v1/leagues/<id>/join` - Join league
- `POST /api/v1/leagues/<id>/invite` - Send invitation
- `GET/POST /api/v1/leagues/<id>/picks` - Get/submit picks
- `GET /api/v1/leagues/<id>/picks/<tournamentId>/available-players` - Available players
- `GET /api/v1/leagues/<id>/standings` - League standings
- `GET /api/v1/leagues/<id>/scoring/<tournamentId>` - Scoring breakdown

### Favorites
- `GET/POST /api/v1/favorites` - Get/add favorites
- `DELETE /api/v1/favorites/<id>` - Remove favorite

### Other
- `POST /api/v1/users` - Register/update user
- `POST /api/v1/slack/events` - Slack event webhook

## Testing Slack Locally

```bash
# Start backend with Slack disabled (default in Docker)
make up

# Test Slack endpoint
curl -XPOST localhost:8080/api/v1/slack/events \
  --data '{"event_id": "test", "event": {"channel": "c", "user": "u", "type": "app_mention", "text": "@Bot player info scheffler masters"}}'

# To test with real Slack, use ngrok:
ngrok http 8080
# Update Slack app event subscription URL to ngrok URL
```

## Key Source Locations

- Web app entry: `web/src/main.tsx`
- React pages: `web/src/pages/`
- API client: `web/src/services/api.ts`
- Auth service: `web/src/services/auth.ts`
- React hooks: `web/src/hooks/`
- Flask routes: `gcp/app-engine/main.py`
- League queries: `gcp/app-engine/league_queries.py`
- Fantasy scoring: `gcp/app-engine/fantasy_scoring.py`
- Slack command handler: `gcp/app-engine/slack_handler.py`
- Firebase auth validation: `gcp/app-engine/auth_utils.py`

## Environment Variables

Create a `.env` file in the project root for Docker:

```bash
# Firebase (for web app)
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...

# API URL (production)
VITE_API_BASE_URL=https://your-app-engine-url.appspot.com

# Google credentials (for backend to access GCP services)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## CI/CD

GitHub Actions workflows:
- `.github/workflows/web.yml` - Web app: lint, test, build, deploy to Firebase Hosting
- `.github/workflows/app_engine.yml` - Backend: lint, test (with Postgres)
- `.github/workflows/refresh_pga_data_function.yml` - Cloud Functions

## File Structure

```
golf-better/
├── docker-compose.yml      # Docker orchestration
├── Makefile                # Convenient Docker commands
├── web/                    # React web app
│   ├── Dockerfile
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   ├── firebase.json       # Firebase Hosting config
│   └── package.json
├── gcp/
│   ├── app-engine/         # Flask backend
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── league_queries.py
│   │   ├── fantasy_scoring.py
│   │   └── test/
│   ├── cloud-functions/    # PGA data sync
│   └── migrations/         # Sqitch PostgreSQL migrations
└── .github/workflows/      # CI/CD
```
