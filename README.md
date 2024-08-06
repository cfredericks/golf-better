# golf-better
![Android](https://github.com/cfredericks/golf-better/actions/workflows/android.yml/badge.svg) ![App Engine](https://github.com/cfredericks/golf-better/actions/workflows/app_engine.yml/badge.svg) ![Refresh PGA Data](https://github.com/cfredericks/golf-better/actions/workflows/refresh_pga_data_function.yml/badge.svg) ![Common](https://github.com/cfredericks/golf-better/actions/workflows/common.yml/badge.svg)

# Local Setup

# Local Setup

To build and run the Android app:
- Install Android Studio and load code
- Login to golf-better GCP account with gcloud
- Run the app in one of these ways:
  - Install an emulator and run from Android Studio
  - Connect a real device (either using USB or "adb tcpip") and run from Android Studio
  - Build an APK and push to a real device

To set up firebase for the first time, you will need to upload the SHA hash of your signing
certificate under Project Settings >> General. See https://developers.google.com/android/guides/client-auth
for the command to get the SHA of the debug certificate.

To setup sqitch, run:
```bash
brew tap sqitchers/sqitch
brew install sqitch --with-postgres-support --with-sqlite-support
```

See directories under /gcp for specific READMEs.

# Repo structure

- [/app](/app) - Android app
  - Also the parent directory [/](/) contains gradle build info
- [/gcp](/gcp) - Other infrastructure/applications to manage the backend database, app engine, etc.
  - [/gcp/app-engine](/gcp/app-engine) - App Engine code for serving data to the Android app
  - [/gcp/cloud-functions/refresh-pga-data](/gcp/cloud-functions/refresh-pga-data) - Cloud Function for periodically syncing PGA APIs into CloudSQL
  - [/gcp/cloud-functions/refresh-leaderboards](/gcp/cloud-functions/refresh-leaderboards) - Cloud Function for periodically syncing tournament leaderboard info from SportsData API into CloudSQL
  - [/gcp/cloud-functions/refresh-tournaments](/gcp/cloud-functions/refresh-tournaments) - Cloud Function for periodically syncing tournament info from SportsData API into CloudSQL
  - [/gcp/migrations](/gcp/migrations) - Sqitch Postgres database migrations
  - [/gcp/scripts](/gcp/scripts) - Ad hoc scripts for maintenance, monitoring, etc.
- [/.github/workflows](/.github/workflows) - CI scripts

# System diagram

![System Diagram](system-diagram.png)
