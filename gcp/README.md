# Running locally

First run:
```bash
pip install -e .
```
from the root of your project directory. This installs the project in "editable" mode, which means that changes to the source files are immediately available without reinstalling.

And then you can run each individual package, e.g.
```bash
python3 app-engine/main.py
```

# Deploying golf-better-common to PyPI

First make sure that you have setup github creds in your ~/.pypirc, e.g.
```
[distutils]
index-servers =
    pypi
    github

[github]
repository: https://github.com/cfredericks/golf-better
username: <username>
password: <password/personal-access-token>
```

```bash
cd common
python3 setup.py sdist bdist_wheel
twine upload -r github dist/*
```

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