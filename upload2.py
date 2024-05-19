import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Authentication
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_account.json"

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

# Optionally create or retrieve playlist based on title
def get_or_create_playlist(youtube, title, description):
    response = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    ).execute()

    for playlist in response['items']:
        if playlist['snippet']['title'].lower() == title.lower():
            return playlist['id']  # Playlist already exists

    # Create new playlist
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    result = request.execute()
    return result['id']

# Upload video and return video ID
def upload_video(youtube, file_path, title, description, playlist_id):
    request_body = {
        'snippet': {
            'categoryId': '22',
            'title': title,
            'description': description,
            'tags': ['family', 'home video']
        },
        'status': {
            'privacyStatus': 'private',
            'selfDeclaredMadeForKids': False,
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))

    video_id = response.get('id')
    add_video_to_playlist(youtube, video_id, playlist_id)
    return video_id

# Add video to the specified playlist
def add_video_to_playlist(youtube, video_id, playlist_id):
    youtube.playlistItems().insert(
        part="snippet",
        body={
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
    ).execute()

def main():
    youtube = youtube_authenticate()
    media_folder_path = r'c:\FamilyVideos'
    playlist_id = input("Enter the Playlist ID (leave blank to create/find based on video filenames): ")

    # Supported video file types
    video_extensions = ['.mp4', '.mov']

    for filename in os.listdir(media_folder_path):
        if any(filename.endswith(ext) for ext in video_extensions):
            file_path = os.path.join(media_folder_path, filename)
            if not playlist_id:  # If no playlist ID provided, determine from filename
                playlist_name = "Default Playlist Name"
                playlist_description = "Default description for videos"
                playlist_id = get_or_create_playlist(youtube, playlist_name, playlist_description)

            title = "Uploaded Video: " + filename
            description = "A family video uploaded automatically."
            video_id = upload_video(youtube, file_path, title, description, playlist_id)
            print(f"Video uploaded with ID: {video_id} to playlist: {playlist_id}")

if __name__ == "__main__":
    main()
