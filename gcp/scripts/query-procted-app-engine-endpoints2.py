from google.auth import jwt
from google.auth.transport.requests import Request
import requests
import json

# Path to your service account key file
key_path = 'key.json'

# Load the service account key file
with open(key_path) as f:
    service_account_info = json.load(f)

# Create credentials using the service account information
audience = 'https://stoked-depth-428423-j7.uc.r.appspot.com'
credentials = jwt.Credentials.from_service_account_info(service_account_info, audience=audience)

# Obtain the identity token
request = Request()
credentials.refresh(request)
identity_token = credentials.token

# Set up the header with the Identity Token
headers = {
    'Authorization': f'Bearer {identity_token}',
    'Content-Type': 'application/json'
}

# Define the data payload for the POST request
data = {
    'key1': 'value1',
    'key2': 'value2'
}

response = requests.post('https://stoked-depth-428423-j7.uc.r.appspot.com/protected/api/v1/refreshTournaments', headers=headers, json=data)
print(response.status_code, response.text)
