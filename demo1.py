from google_apis import create_service

client_secret_file = 'client_account.json'
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']

service = create_service(client_secret_file, API_NAME, API_VERSION, SCOPES)

response = service.albums().list(pageSize=10).execute()
albums = response['albums']
nextPageToken = response.get('nextPageToken')

while nextPageToken:
    print('fetching next page...')
    response = service.albums().list(pageSize=10, pageToken=nextPageToken).execute()
    albums.extend(response['albums'])
    nextPageToken = response.get('nextPageToken')

for album in albums:
    if int(album.get('mediaItemsCount', 0)) > 15:
        print(album['id'])
        print(album['title'])
        print(album.get('mediaItemsCount',0)) 
        print()