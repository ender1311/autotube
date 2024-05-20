import os
import pickle
import re
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Authentication function
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.force-ssl"]
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

# Function to update video title and add to new playlist
def copy_video_to_new_playlist(youtube, video_id, original_date, new_playlist_id):
    # Formulate new title based on the date
    new_title = f"{original_date}"

    # Update video title
    youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": {
                "title": new_title,
                "categoryId": "22"  # Update category if necessary
            }
        }
    ).execute()

    # Add video to the new playlist
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": new_playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()
    print(f"Video with ID {video_id} copied to new playlist and renamed to '{new_title}'")

def main():
    youtube = youtube_authenticate()
    old_playlist_id = "PLMMP1qy1ZjNRlxQqRBW3CmwhOsIfccki5"  # Abigail and Emmy playlist
    new_playlist_id = "PLMMP1qy1ZjNSqtE136jJlE7LdlWnyPCNz"  # 2024 Q2

    # Fetch the first video from the old playlist
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=old_playlist_id,
        maxResults=1
    )
    response = request.execute()

    if response.get('items'):
        video_id = response['items'][0]['snippet']['resourceId']['videoId']
        published_date = response['items'][0]['snippet']['publishedAt'][:10]  # Get YYYY-MM-DD
        copy_video_to_new_playlist(youtube, video_id, published_date, new_playlist_id)
    else:
        print("No videos found in the playlist.")

if __name__ == "__main__":
    main()
