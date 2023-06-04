import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, generate_container_sas, ContentSettings
from dotenv import load_dotenv

class FileManager:
    def __init__(self, dir_path: str = 'uploaded_files'):
        load_dotenv()

        self.dir_path = dir_path

    def upload_file(self, bytes_data, file_name, data_type='wb'):
        file_url = os.path.join(self.dir_path, file_name)
        with open(file_url, data_type) as f:
            f.write(bytes_data)
        return file_url
        
    def get_all_files(self):
        files = os.listdir(self.dir_path)
        files = [{'filename': file, 'embeddings_added': True, 'fullpath': file} for file in files if file != '.DS_Store']

        return files 

    def upsert_blob_metadata(self, file_name, metadata):
        pass
