from s3_manager import S3Manager
from decouple import config
from db_operations import DBOperations
from utility import embed_data, recursive_text_splitter
import os
import shutil
from enum_utility import Bucket
from file_operations import FileOperations

S3_DOWNLOAD_PREFIX = config('S3_DOWNLOAD_PREFIX')
BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')


def handler():
    try:
        s3_manager = S3Manager()
        file_ops = FileOperations()
        list_of_files = s3_manager.get_all_objects(prefix=S3_DOWNLOAD_PREFIX, bucket=Bucket.RESOURCES_BUCKET.value)
        print(list_of_files)
        print(len(list_of_files))
        print("---------------------------------------------------------------------------------------------")

        for file in list_of_files[1:]:
            file_name = file.split("/")[-1]
            class_id = file_name.split("_")[0]

            print(f"downloading the transcript file form s3 for {class_id}.....")
            download_folder = f'{BASE_TRANSCRIPT_PATH}{class_id}/'
            os.makedirs(download_folder, exist_ok=True)
            s3_manager.download_file_from_s3(key=file, download_path=f"{download_folder}{file_name}", bucket=Bucket.RESOURCES_BUCKET.value)

            print("load and split the content from the transcript.....")
            pages = file_ops.load_text_file(class_id=class_id)

            print(f"splitting transcription {file_name}.....")
            docs = recursive_text_splitter(pages)

            print(f"embedding splits for {file_name}.....")
            db_ops = DBOperations()
            section = db_ops.get_section_id(class_id=class_id)

            if embed_data(docs, section=section, class_id=class_id):
                print(f"updating transcription status in db for {class_id}.....")
                db_ops.update_transcription_status(class_id=class_id, status=1)
                print("embedding completed, deleting file from local.....")
                shutil.rmtree(f"{BASE_TRANSCRIPT_PATH}{class_id}")
            print("--------------------------------------------------------------------------------------------")

    except Exception as err:
        print(f"Here is the issue: {err}")


handler()
