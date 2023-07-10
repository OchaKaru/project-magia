from io import BytesIO
from mimetypes import guess_type
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class DriveAPI:
    def __init__(self, cred_file: str):
        with open(cred_file, 'r') as file:
            creds_json = json.loads(file.read())
            creds = Credentials(
                None,
                refresh_token = creds_json['refresh_token'],
                token_uri = creds_json['token_uri'],
                client_id = creds_json['client_id'],
                client_secret = creds_json['client_secret']
            )
            self.service_client = build('drive', 'v3', credentials = creds)
            
    def _check_mimetype(self, mimetype: str) -> str:
        if mimetype is None:
            mimetype = guess_type(media_file)
            if mimetype is None:
                return None
        return mimetype
    
    def _send_chunks(self, request) -> dict:
        response = None
        while response is None:
            status, response = request.next_chunk()
            # if status:
            #     load_status(status.progress(), 'Upload')
        return response
    
    def _receive_chunks(self, request) -> BytesIO:
        file = BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # load_status(status.progress(), 'Download')
            
        return file
    
    def multipart_upload(self, media_file: str, metadata: dict = None, mimetype: str = None) -> str:
        if self._check_mimetype(mimetype) is None:
            return None
        
        media_to_upload = MediaFileUpload(media_file, mimetype = mimetype)
        
        response = self.service_client.files().create(body = metadata, media_body = media_to_upload, fields = 'id').execute()
        
        return response['id']
        
    
    def resumable_upload(self, media_file: str, metadata: dict = None, mimetype: str = None, chunksize: int = 262144) -> str:
        if self._check_mimetype(mimetype) is None:
            return None
                    
        media_to_upload = MediaFileUpload(media_file, mimetype = mimetype, resumable = True, chunksize = chunksize)
        
        request = self.service_client.files().create(body = metadata, media_body = media_to_upload, fields = 'id')
        response = self._send_chunks(request)
        
        return response['id']

    def download(self, file_id) -> BytesIO:
        request = self.service_client.files().get_media(fileId = file_id)
        return self._receive_chunks(request)
    
    def delete(self, file_id):
        self.service_client.files().delete(fileId = file_id).execute()
        
if __name__ == '__main__':
    google_drive = DriveAPI('../../sessions/google-drive-cred.json')
    google_drive.multipart_upload('../../driver.py', metadata = {'name': 'driver.py'}, mimetype = 'text/plain')