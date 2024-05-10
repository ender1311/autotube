from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for the authorization
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def create_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', scopes=SCOPES)
    credentials = flow.run_local_server(port=0)
    service = build('photoslibrary', 'v1', credentials=credentials)
    return service

service = create_service()
