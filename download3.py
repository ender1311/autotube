import time
import requests
import os
import datetime
from google_apis import create_service
# Parameters
download_folder = r'd:\fam_vid'  # Raw string for the path
max_videos = 5  # Adjust the limit as needed
timeout_seconds = 5 

# API service setup
client_secret_file = 'client_account.json'
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

service = create_service(client_secret_file, API_NAME, API_VERSION, SCOPES)

def download_videos(service, download_folder, max_videos, timeout=timeout_seconds):
    videos = []
    nextPageToken = None
    start_time = time.time()
    download_count = 0

    while True:
        if time.time() - start_time > timeout:
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

    for video in videos:
        if download_count >= max_videos:
            print(f"Reached the maximum limit of {max_videos} downloads.")
            break

        creation_date = datetime.datetime.strptime(video['mediaMetadata']['creationTime'], '%Y-%m-%dT%H:%M:%SZ')
        year_folder = os.path.join(download_folder, str(creation_date.year))
        quarter = (creation_date.month - 1) // 3 + 1
        quarter_folder = os.path.join(year_folder, f'Q{quarter}')
        if not os.path.exists(quarter_folder):
            os.makedirs(quarter_folder)

        base_url = video['baseUrl'] + "=dv"
        response = requests.get(base_url)
        if response.status_code == 200:
            file_extension = os.path.splitext(video['filename'])[1]
            new_filename = creation_date.strftime('%Y.%m.%d') + file_extension
            new_file_path = os.path.join(quarter_folder, new_filename)

            counter = 1
            while os.path.exists(new_file_path):
                new_filename = creation_date.strftime('%Y.%m.%d') + f".{chr(64 + counter)}" + file_extension
                new_file_path = os.path.join(quarter_folder, new_filename)
                counter += 1

            with open(new_file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded and saved {video['filename']} as {new_filename} successfully.")
            download_count += 1
        else:
            print(f"Failed to download {video['filename']}.")



# Execute the function
download_videos(service, download_folder, max_videos)
