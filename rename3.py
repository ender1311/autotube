import os
import pickle
import json
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load Playlist IDs
with open('old_playlist.json', 'r') as f:
    old_playlist = json.load(f)
with open('new_playlists.json', 'r') as f:
    new_playlists = json.load(f)

# Authenticate with YouTube API
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

# Determine the correct quarterly playlist based on date
def determine_playlist(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    quarter = (date_obj.month - 1) // 3 + 1
    year_quarter = f"{date_obj.year} Q{quarter}"
    return new_playlists.get(year_quarter)

# Function to update video title and add to new playlist
def process_video(youtube, video_id, video_title, date, log_dict, new_playlist_id):
    suffix = 'a'
    new_title_base = f"{date} {suffix}"
    suffix_count = 0

    # Create a set of existing titles in the target playlist from the log
    existing_titles = set(log['new_title'] for log in log_dict if log['new_playlist_id'] == new_playlist_id)

    # Generate a unique new title by appending a suffix if the proposed title already exists
    while new_title_base in existing_titles:
        suffix_count += 1
        new_title_base = f"{date} {chr(ord(suffix) + suffix_count)}"  # Increment character suffix

    # Update the video title
    youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": {
                "title": new_title_base,
                "categoryId": "22"
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

    # Log the video processing, including playlist title
    new_playlist_title = next((title for title, id in new_playlists.items() if id == new_playlist_id), "Unknown Playlist")
    log_dict.append({
        "video_id": video_id,
        "date": date,
        "new_title": new_title_base,
        "new_playlist_id": new_playlist_id,
        "new_playlist_title": new_playlist_title,
        "processed": True
    })
    print(f"Video titled '{video_title}' copied to new playlist '{new_playlist_title}' and renamed to '{new_title_base}'")

def main():
    youtube = youtube_authenticate()
    old_playlist_id = old_playlist['old_playlist_id']
    log_file_path = "video_processing_log.json"

    # Load existing log or create a new one
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            log_dict = json.load(file)
    else:
        log_dict = []

    # Ask user for the number of videos they want to process
    num_videos = int(input("Enter the number of videos to process: "))

    # Fetch videos from the old playlist
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=old_playlist_id,
        maxResults=num_videos
    )
    response = request.execute()

    for item in response.get('items', []):
        video_id = item['snippet']['resourceId']['videoId']
        video_title = item['snippet']['title']
        published_date = item['snippet']['publishedAt'][:10]  # Get YYYY-MM-DD
        
        # Determine the new playlist ID based on the date
        new_playlist_id = determine_playlist(published_date)
        if not new_playlist_id:
            print(f"No playlist found for the date {published_date}.")
            continue

        # Check if the video has already been processed
        if any(log['video_id'] == video_id for log in log_dict):
            print(f"Video titled '{video_title}' has already been processed.")
            continue

        process_video(youtube, video_id, video_title, published_date, log_dict, new_playlist_id)

    # Save the updated log
    with open(log_file_path, 'w') as file:
        json.dump(log_dict, file, indent=4)

if __name__ == "__main__":
    main()
