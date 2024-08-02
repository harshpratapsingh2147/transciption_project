from s3_manager import S3Manager
from decouple import config
from langchain.document_loaders import TextLoader
from db_operations import DBOperations
from utility import embed_data, recursive_text_splitter
import os
import shutil


S3_DOWNLOAD_PREFIX = config('S3_DOWNLOAD_PREFIX')
BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')


def handler():
    try:
        s3_manager = S3Manager()
        list_of_files = s3_manager.get_all_objects(prefix=S3_DOWNLOAD_PREFIX)
        print(list_of_files)
        print(len(list_of_files))
        for file in list_of_files[1:]:
            file_name = file.split("/")[-1]
            class_id = file_name.split("_")[0]
            print(class_id)
            download_folder = f'{BASE_TRANSCRIPT_PATH}{class_id}/'
            os.makedirs(download_folder, exist_ok=True)
            s3_manager.download_transcript_from_s3(key=file, download_path=f"{download_folder}{file_name}")
            print("\n--------------------load and split the content from the transcript-----------------------------\n")
            loader = TextLoader(f"{BASE_TRANSCRIPT_PATH}{class_id}/{file_name}")
            pages = loader.load()
            print(f"splitting transcription {file_name}.....")
            docs = recursive_text_splitter(pages)
            print(f"embedding splits for {file_name}.....")
            db_ops = DBOperations()
            section = db_ops.get_section_id(class_id=class_id)

            if embed_data(docs, section=section, class_id=class_id):
                print(f"\n-----------------updating transcription status in db for {class_id}---------------------\n")
                db_ops.update_transcription_status(class_id=class_id)
                print("embedding completed............deleting file from local")
                shutil.rmtree(f"{BASE_TRANSCRIPT_PATH}{class_id}")
    except Exception as err:
        print(f"Here is the issue: {err}")


handler()
