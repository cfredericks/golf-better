# golf-better

To build app:
- Install Android Studio and load code
- Set API_KEY in com.cfredericks.golfbetter.SportsDataApiClient
- Install an emulator for running the code (or build an APK and push to a real device)

See directories under /gcp for specific READMEs.

# Repo structure

- `/app` - Android app
  - Also the parent `/` directory contains gradle build info
- `/gcp` - Other infrastructure/applications to manage the backend database, app engine, etc.
  - `/gcp/golf-better-app-engine` - App Engine code for serving data to the Android app
  - `/gcp/golf-better-refresh-tourns-func` - Cloud Function for periodically syncing tournament info from SportsData API into CloudSQL
  - `/gcp/golf-better-scripts` - Ad hoc scripts for maintenance, monitoring, etc.
  - TODO: Move other infra to repo in spirit of IaC (i.e. CloudSQL, service accounts, CRON scheduler, GSM secrets, etc.)
- `/.github/workflows` - CI scripts

![System Diagram](system-diagram.png)