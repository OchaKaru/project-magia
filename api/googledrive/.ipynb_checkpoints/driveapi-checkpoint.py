import json

from mimetypes import guess_type

from io import BytesIO

from sys import getsizeof
from os.path import exists, getsize

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

client_id = '647242426283-qqi6fhs3ab3ov89is1ijjq55e26ub2bt.apps.googleusercontent.com'
client_secret = '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'
token_uri = 'https://oauth2.googleapis.com/token'

redirect_uri = 'https://developers.google.com/oauthplayground'
refresh_token = '1//04InU8yfTQhXuCgYIARAAGAQSNwF-L9IrrcsB0410vcBeGqYdkcwBFin_Fzjkfm1HNC7wLcEVpteDRmZ0c9wg1Zr7ZfcidWHFRnM'

class DriveAPIManager:
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
            self.mimetyper = Magic(mime = True)
    
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
    
    def resumable_upload(self, media_file: str, metadata = None: dict, mimetype = None : str, chunksize = 262144 : int) -> str:
        if mimetype is None:
            mimetype = guess_type(media_file)
            if mimetype is None:
                raise MimeTypeNotFoundError
                    
        media_to_upload = MediaFileUpload(media_file, mimetype = mimetype, resumable = True, chunksize = chunksize)
        
        request = service_client.files().create(body = metadata, media_body = media_to_upload, fields = 'id')
        response = self._send_chunks(request)
        
        return response['id']

    def download(self, file_id) -> BytesIO:
        request = service_client.files().get_media(fileId=model_file_id)
        return self._receive_chunks(request)
    
    def delete(self, file_id):
        service_client.files().delete(fileId = file_id).execute()