from decouple import config
from enum_utility import Bucket
from s3_manager import S3Manager
from db_operations import DBOperations
from file_operations import FileOperations
from pdf_to_text_utility import PDFToTextUtilityManager
import os

S3_DOWNLOAD_PREFIX = config('S3_DOWNLOAD_PREFIX')
BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
BASE_PDF_PATH = config('BASE_PDF_PATH')
BASE_TEXT_PATH = config('BASE_TEXT_PATH')

def add_handouts():
    try:
        s3_manager = S3Manager()
        list_of_files = s3_manager.get_all_objects(prefix=S3_DOWNLOAD_PREFIX, bucket=Bucket.RESOURCES_BUCKET.value)
        db_ops = DBOperations()
        file_ops = FileOperations()

        for file in list_of_files[1:2]:
            file_name = file.split("/")[-1]
            class_id = file_name.split("_")[0]
            print(f"--------------getting the handout file name for {class_id}--------------------")
            handout_loc = db_ops.fetch_handout_file_name_from_db(class_id=class_id)

            if handout_loc:
                handout_download_folder = f"{BASE_PDF_PATH}"
                os.makedirs(handout_download_folder, exist_ok=True)
                print(f"-----------downloading the handout file for {class_id}--------------------")
                s3_manager.download_file_from_s3(
                    key=f"classroom/handouts/{handout_loc}",
                    download_path=f"{handout_download_folder}{handout_loc}",
                    bucket=Bucket.ASSETS_BUCKET.value
                )

                print(f"-----downloading the transcript file for {class_id} from s3--------------")
                transcript_download_folder = f'{BASE_TRANSCRIPT_PATH}{class_id}/'
                os.makedirs(transcript_download_folder, exist_ok=True)
                s3_manager.download_file_from_s3(
                    key=file,
                    download_path=f"{transcript_download_folder}{file_name}",
                    bucket=Bucket.RESOURCES_BUCKET.value
                )
                print(f"--------converting the handout pdf to text for {class_id}----------------")
                utility_manager = PDFToTextUtilityManager(s3_pdf_file_path=f"classroom/handouts/{handout_loc}")
                handout_content = utility_manager.pdf_processing()
                print(f"--------writing content to transcript file for {class_id}----------------")
                file_ops.write_content_to_file(
                    content=f"\n Class Notes: \n {handout_content}",
                    class_id=class_id,
                    file_name=file_name
                )
                print(f"--------uploading the updated transcript file on s3 {class_id}-----------")
                s3_upload_path = f"ai_live_query_resolution/gemini_improved_transcripts/{file_name}"
                s3_manager.upload_file_on_s3(
                    local_file_path=f"{transcript_download_folder}{file_name}",
                    s3_upload_path=s3_upload_path,
                    bucket=Bucket.RESOURCES_BUCKET.value
                )
            else:
                print("No handout was found for lecture")

    except Exception as err:
        print(f"Here is the issue: {err}")

add_handouts()