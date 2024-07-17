import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import requests

# Path to your service account key file
key_path = 'key.json'

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=['https://www.googleapis.com/auth/cloud-platform'])

# Request to obtain an Identity Token for IAP
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
