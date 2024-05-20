import os
import pickle
import re
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Authentication function
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
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

# Function to get playlist ID by name
def get_playlist_id(youtube, playlist_name):
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()
    for item in response.get('items', []):
        if item['snippet']['title'].lower() == playlist_name.lower():
            return item['id']
    return None

# Function to list videos in a playlist and print their date information
def list_videos_in_playlist(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=3  # Limit to 5 videos
    )
    response = request.execute()

    for item in response.get('items', []):
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        published_date = item['snippet']['publishedAt']

        # Attempt to extract date from the title if no published date
        date_from_title = re.search(r"\b(\d{1,2}/\d{1,2}/\d{2})\b", title)
        if date_from_title:
            date = datetime.strptime(date_from_title.group(), '%m/%d/%y').date()
        else:
            date = published_date[:10]  # Slice to get only the YYYY-MM-DD part

        print(f"Title: {title}")
        print(f"Date: {date}\n")

def main():
    youtube = youtube_authenticate()
    playlist_name = input("Enter the Playlist name: ")
    playlist_id = get_playlist_id(youtube, playlist_name)
    
    if playlist_id:
        print(f"Found playlist '{playlist_name}' with ID: {playlist_id}")
    else:
        print(f"No playlist found with the name '{playlist_name}'")

if __name__ == "__main__":
    main()
