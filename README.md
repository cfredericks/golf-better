# golf-better
![Android CI Status](https://github.com/cfredericks/golf-better/actions/workflows/android.yml/badge.svg)

To build app:
- Install Android Studio and load code
- Set API_KEY in com.cfredericks.golfbetter.SportsDataApiClient
- Install an emulator for running the code (or build an APK and push to a real device)

See directories under /gcp for specific READMEs.

# Repo structure

- [/app](/app) - Android app
  - Also the parent directory [/](/) contains gradle build info
- [/gcp](/gcp) - Other infrastructure/applications to manage the backend database, app engine, etc.
  - [/gcp/app-engine](/gcp/app-engine) - App Engine code for serving data to the Android app
  - [/gcp/cloud-functions/refresh-leaderboards](/gcp/cloud-functions/refresh-leaderboards) - Cloud Function for periodically syncing tournament leaderboard info from SportsData API into CloudSQL
  - [/gcp/cloud-functions/refresh-tournaments](/gcp/cloud-functions/refresh-tournaments) - Cloud Function for periodically syncing tournament info from SportsData API into CloudSQL
  - [/gcp/scripts](/gcp/scripts) - Ad hoc scripts for maintenance, monitoring, etc.
  - TODO: Move other infra to repo in spirit of IaC (i.e. CloudSQL, service accounts, CRON scheduler, GSM secrets, etc.)
- [/.github/workflows](/.github/workflows) - CI scripts

![System Diagram](system-diagram.png)