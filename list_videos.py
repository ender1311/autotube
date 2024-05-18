import time
from google_apis import create_service

# API service setup
client_secret_file = 'client_account.json'
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary']

service = create_service(client_secret_file, API_NAME, API_VERSION, SCOPES)
timeout_seconds = 3

# Function to search for video media items with a 10-second timeout and print their sizes
def list_videos(service, timeout=timeout_seconds):
    videos = []
    nextPageToken = None
    start_time = time.time()  # Record the start time

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
        
        if not nextPageToken:
            break

    return videos

# Fetch and print video details including file size
videos = list_videos(service)
for video in videos:
    video_id = video['id']
    filename = video['filename']
    product_url = video['productUrl']
    # Retrieve and display the video's size from mediaMetadata if available
    video_size = video.get('mediaMetadata', {}).get('video', {}).get('fileSize', 'Not available')
    
    print(f"ID: {video_id}")
    print(f"Filename: {filename}")
    print(f"Product URL: {product_url}")
    print(f"Video Size: {video_size} bytes")
    print()

