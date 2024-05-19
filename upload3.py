import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Authentication function
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
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
    return response['id']

# Upload video and return video ID
def upload_video(youtube, file_path, title, description, playlist_id):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['sample', 'video', 'upload'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'unlisted'
        }
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

    response = None
    while response is None:
        status, response = upload_request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
    video_id = response.get('id')
    print(f'Video {title} uploaded with ID: {video_id}')

    # Add video to playlist
    add_video_to_playlist(youtube, video_id, playlist_id)
    print(f"Added video {title} to playlist {name}")

    return video_id

# Add video to the specified playlist
def add_video_to_playlist(youtube, video_id, playlist_id):
    playlist_item_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    playlist_item_request.execute()

def main():
    youtube = youtube_authenticate()
    media_folder_path = r'c:\FamilyVideos'
    file_name = input("Enter the file name of the video to upload: ")
    file_path = os.path.join(media_folder_path, file_name)

    name = input("Enter the name of the playlist: ")
    description = input("Enter the description of the playlist: ")
    playlist_id = create_playlist(youtube, name, description)

    # Assuming video details could be based on the file name or static
    title = "Uploaded Video: " + file_name
    video_description = "Automatically uploaded video."

    upload_video(youtube, file_path, title, video_description, playlist_id)

if __name__ == "__main__":
    main()
