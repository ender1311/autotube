import datetime
from google_apis import create_service
from googleapiclient.http import MediaFileUpload

CLIENT_SECRET_FILE = 'client_account.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

mediaFilePath = r"C:\FamilyVideos\2023.06.08.mov"
mediaFile = MediaFileUpload(mediaFilePath)
# thumbnailFilePath = r'd:\fam_vid\thumbnail.png'
service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

upload_date_time = datetime.datetime(2020, 12, 25, 12, 30, 0).isoformat() + '.000Z'

request_body = {
    'snippet': {
        'categoryI': 19,
        'title': 'Upload Testing',
        'description': 'Hello World Description',
        'tags': ['Travel', 'video test', 'Travel Tips']
    },
    'status': {
        'privacyStatus': 'private',
        'publishAt': upload_date_time,
        'selfDeclaredMadeForKids': False, 
    },
    'notifySubscribers': False
}



response_upload = service.videos().insert(
    part='snippet,status',
    body=request_body,
    media_body=mediaFile
).execute()

# Print the video ID after upload
print("Uploaded video ID:", response_upload.get('id'))

# service.thumbnails().set(
#     videoId=response_upload.get('id'),
#     media_body=MediaFileUpload(thumbnailFilePath)
# ).execute()