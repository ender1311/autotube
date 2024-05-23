import os
import pickle
import json
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Authentication function
def youtube_authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube"]
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

# Update or append new playlist ID to JSON file
def update_new_playlists_json(playlist_title, playlist_id):
    try:
        with open('new_playlists.json', 'r+') as file:
            playlists = json.load(file)
            playlists[playlist_title] = playlist_id  # Update or add new playlist
            file.seek(0)
            json.dump(playlists, file, indent=4)
            file.truncate()
    except FileNotFoundError:
        with open('new_playlists.json', 'w') as file:
            json.dump({playlist_title: playlist_id}, file, indent=4)

# Function to get or create playlist ID by name
def get_or_create_playlist(youtube, playlist_name):
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()
    for item in response.get('items', []):
        if item['snippet']['title'].lower() == playlist_name.lower():
            return item['id']

    # If playlist not found, create it
    body = {
        "snippet": {
            "title": playlist_name,
            "description": "Automatically created playlist."
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    try:
        response = youtube.playlists().insert(part="snippet,status", body=body).execute()
        playlist_id = response['id']
        update_new_playlists_json(playlist_name, playlist_id)
        return playlist_id
    except HttpError as error:
        print(f"Failed to create playlist: {error}")
        return None


# Update or append new playlist ID to JSON file
def update_new_playlists_json(playlist_title, playlist_id):
    # Path to the JSON file
    json_file_path = 'new_playlists.json'
    
    # Read the existing data
    try:
        with open(json_file_path, 'r') as file:
            playlists = json.load(file)
    except FileNotFoundError:
        playlists = {}  # If the file does not exist, start with an empty dictionary

    # Update the dictionary with the new playlist ID
    playlists[playlist_title] = playlist_id

    # Write the updated dictionary back to the file
    with open(json_file_path, 'w') as file:
        json.dump(playlists, file, indent=4)

# Example usage within the main script
def main():
    youtube = youtube_authenticate()
    playlist_name = input("Enter the Playlist name: ")
    playlist_id = get_or_create_playlist(youtube, playlist_name)
    
    if playlist_id:
        print(f"Playlist '{playlist_name}' is ready with ID: {playlist_id}")
        update_new_playlists_json(playlist_name, playlist_id)  # Update the JSON file with the new ID
    else:
        print(f"Failed to prepare playlist named '{playlist_name}'")

if __name__ == "__main__":
    main()

