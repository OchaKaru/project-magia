# download the file using google api
# clean the text using the function from util
# upload the file using google api and creating a new file from the content
# delete old id and change for new file id
import json

from modeltraining.api.googledrive.driveapi import DriveAPI
from modeltraining.util.datacleaning import clean_data

service = DriveAPI("./sessions/google-drive-cred.json")
dataloc_json = json.load(open("./sessions/modelinfo/dataloc.json", 'r'))

for corpus_type in ["anime", "manga", "games"]:
    text = service.download(dataloc_json['corpus_drive_ids'][corpus_type]).getvalue().decode('UTF-8')
    text = clean_data(text)
    
    metadata = {'name': f"{corpus_type}_corpus.txt", 'parents': ['1SOXyHF6HxfXSjXZJv9Kk0IRYG8DYLVO5']}
    
    new_id = service.create(text, metadata = metadata, mimetype = 'text/plain')
    service.delete(dataloc_json['corpus_drive_ids'][corpus_type])
    dataloc_json['corpus_drive_ids'][corpus_type] = new_id
    
    print(f"Completed {corpus_type}...")
    
json.dump(dataloc_json, open("./sessions/modelinfo/dataloc.json", 'w', 'utf-8'))