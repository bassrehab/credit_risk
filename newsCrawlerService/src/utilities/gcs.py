from google.cloud import storage
import os
import csv
from io import StringIO
from newsCrawlerService.src.config.params import params

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = params["gcp_credentials"]


def upload_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


def download_gcs(bucket_name, remote_blob_name):
    """
    Download GCS blob and return as a String
    :param bucket_name:
    :param remote_blob_name:
    :return:
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(remote_blob_name)
    blob = blob.download_as_string()
    blob = blob.decode('utf-8')

    blob = StringIO(blob)  # tranform bytes to string here
    # csv.reader(blob)
    return blob


# --------------------------------------------

if __name__ == "__main__":
    upload_gcs('test-eep-gcs', '../../output/urls_j.c. penney_1627277663.691107.json',
               'folder1/folder2/urls_j.c. penney_1627277663.691107.json')
