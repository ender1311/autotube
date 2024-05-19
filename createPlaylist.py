import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Authentication function
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"

    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server(port=8080)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build(api_service_name, api_version, credentials=credentials)

# Function to create a YouTube playlist
def create_playlist(youtube, name, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": name,
                "description": description
            },
            "status": {
                "privacyStatus": "private"  # or 'public' or 'unlisted'
            }
        }
    )
    response = request.execute()
    print(f"Playlist '{name}' created with ID: {response['id']}")

def main():
    youtube = youtube_authenticate()
    name = input("Enter the name of the playlist: ")
    description = input("Enter the description of the playlist: ")

    create_playlist(youtube, name, description)

if __name__ == "__main__":
    main()
