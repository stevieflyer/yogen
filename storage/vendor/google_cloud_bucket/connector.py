from typing import Optional

from google.cloud import storage
from google.oauth2 import service_account


class GoogleCloudBucketConnector:
    """
    Google Cloud Storage Bucket Connector

    This class is used to connect to the Google Cloud Storage Bucket.
    """
    def __init__(self, bucket_name: str, project_id: Optional[str] = 'double-approach-404515') -> None:
        self.bucket_name = bucket_name
        credentials = service_account.Credentials.from_service_account_file('./gcpStorageCredentials.json')
        self.client = storage.Client(project=project_id, credentials=credentials)
        pass

    def upload_file(self, file_path: str) -> str:
        import time
        import random

        # Get the bucket
        bucket = self.client.get_bucket(self.bucket_name)

        filename = str(int(time.time())) + str(random.randint(10 ** 5, 10 ** 6))

        # Upload the picture
        blob = bucket.blob(filename)
        blob.upload_from_filename(file_path)

        return filename


__all__ = ['GoogleCloudBucketConnector']
