import time
from google_apis import create_service

# API service setup
client_secret_file = 'client_account.json'
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary']

service = create_service(client_secret_file, API_NAME, API_VERSION, SCOPES)
timeout_seconds = 10

# Function to search for video media items with a 10-second timeout and print raw data
def list_videos(service, timeout=timeout_seconds):
    videos = []
    nextPageToken = None
    start_time = time.time()  # Record the start time

    while True:
        if time.time() - start_time > timeout:  # Check if 10 seconds have passed
            print("Timeout reached, stopping search.")
            break
        
        search_body = {
            'pageSize': 5,  # Reduced page size for demonstration
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
        
        if not nextPageToken:
            break

    return videos

# Fetch and print raw video details
videos = list_videos(service)
for video in videos:
    print(video)  # Print the entire dictionary for each video
    print()  # Add a blank line for better readability

