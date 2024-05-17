import time
import requests
import os
from google_apis import create_service

# Specify the download folder and maximum number of videos to download
download_folder = 'd:\\fam_vid'
max_videos = 2  # Limit videos
timeout_seconds = 3 # Limit search time

# API service setup
client_secret_file = 'client_account.json'
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

service = create_service(client_secret_file, API_NAME, API_VERSION, SCOPES)


# Function to search and download a limited number of video media items
def download_videos(service, download_folder, max_videos, timeout=timeout_seconds):
    videos = []
    nextPageToken = None
    start_time = time.time()  # Record the start time
    download_count = 0  # Track the number of downloads

    while True:
        if time.time() - start_time > timeout:  # Check if 10 seconds have passed
            print("Timeout reached, stopping search.")
            break

        search_body = {
            'pageSize': 25,
            'pageToken': nextPageToken,
            'filters': {
                'mediaTypeFilter': {
                    'mediaTypes': ['VIDEO']
                }
            }
        }
        response = service.mediaItems().search(body=search_body).execute()
        videos.extend(response.get('mediaItems', []))
        nextPageToken = response.get('nextPageToken')

        if not nextPageToken or download_count >= max_videos:
            break

    # Check and create download folder if not exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Download videos up to the max_videos limit
    for video in videos:
        if download_count >= max_videos:
            print(f"Reached the maximum limit of {max_videos} downloads.")
            break

        base_url = video['baseUrl'] + "=dv"  # Append '=dv' to get the video download URL
        response = requests.get(base_url)
        if response.status_code == 200:
            with open(os.path.join(download_folder, video['filename']), 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {video['filename']} successfully.")
            download_count += 1
        else:
            print(f"Failed to download {video['filename']}.")


# Fetch and download video details
download_videos(service, download_folder, max_videos)
