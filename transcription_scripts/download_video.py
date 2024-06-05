from google.cloud import storage
import datetime
import requests
import os
from decouple import config

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config('GOOGLE_APPLICATION_CREDENTIALS_PATH')

BASE_DOWNLOAD_PATH = config('BASE_DOWNLOAD_VIDEO_PATH')
GCP_BUCKET = config('GCP_BUCKET')
GCP_DIRECTORY = config('GCP_DIRECTORY')


def download_file(signed_url, class_id):
    try:
        response = requests.get(signed_url, stream=True)

        download_file_path = f"{BASE_DOWNLOAD_PATH}{class_id}.mp4"
        with open(download_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        print("Video downloaded successfully!")
        return True
    except Exception as err:
        print(err)
        return False


def list_files_in_directory(bucket, directory_path):
    file_name_list = []
    blobs = list(bucket.list_blobs(prefix=directory_path))
    for blob in blobs:
        file_name_list.append(blob)
    return file_name_list


def get_signed_url(embed_code_id):
    # Create a storage client
    storage_client = storage.Client()

    # Specify the bucket name and directory path
    bucket_name = GCP_BUCKET
    directory_path = f"{GCP_DIRECTORY}{embed_code_id}"

    # Specify the file name
    file_name = f"{GCP_DIRECTORY}{embed_code_id}/144p.mp4"
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Get the blob (file) from the bucket
    blob = bucket.blob(file_name)

    # Check if the file exists

    file_list = list_files_in_directory(bucket, directory_path)

    if len(file_list) > 0:

        if blob.exists():

            # Generate signed URL with expiration time (in this case, 1 hour from now)
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

            signed_url = blob.generate_signed_url(
                version="v2",
                expiration=expiration_time,
                method="GET"
            )

            return signed_url

        else:
            file_name = f"{GCP_DIRECTORY}{embed_code_id}/360p.mp4"
            blob = bucket.blob(file_name)

            # Generate signed URL with expiration time (in this case, 1 hour from now)
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

            signed_url = blob.generate_signed_url(
                version="v2",
                expiration=expiration_time,
                method="GET"
            )

            return signed_url
    else:
        return None



