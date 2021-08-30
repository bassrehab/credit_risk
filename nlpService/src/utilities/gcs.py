import logging
import traceback

from google.cloud import storage


def upload_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )
    except Exception as e:
        logging.error(traceback.format_exc())


def download_gcs(bucket_name, remote_blob_name, local_file_name):
    """
    Download GCS blob and return as a String
    :param bucket_name:
    :param remote_blob_name:
    :return:
    """
    f = open(local_file_name, "a")
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(remote_blob_name).download_as_string()

        f.write(blob.decode("utf-8"))
        print(
            "Completed fetching remote file named " + bucket_name + "/" + remote_blob_name + " to local file " + local_file_name + ". Wrote " + str(
                len(blob)) + " bytes.")
        download_status = True

    except Exception as e:
        logging.error(traceback.format_exc())
        download_status = False

    finally:
        f.close()

    return download_status
