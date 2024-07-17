# Deploy

Usually you will edit in the GCP console and test changes before deploying there,
but you can manually create a function using somthing like:

```bash
gcloud functions deploy refresh-tourns \
    --runtime python39 \
    --gen2 \
    --trigger-http \
    --set-env-vars 'INSTANCE_CONNECTION_NAME=stoked-depth-428423-j7:us-central1:golf-better,DB_USER=postgres,DB_NAME=postgres' \
    --vpc-connector my-connector \
    --region us-central1
```

# Run locally

```bash
pip3 install -r requirements.txt
python3 main.py
```