from vertexai.generative_models import GenerativeModel, Part
from vertexai import generative_models
from moviepy.editor import *
from decouple import config
import pandas as pd
import sys
import multiprocessing
from db_operations import DBOperations
from download_video import download_file_from_gcp, get_signed_url, download_file_from_s3_using_excel
from gpt_utility import GPTManager
from utility import embed_data, recursive_text_splitter
from file_operations import FileOperations
from s3_manager import S3Manager
from enum_utility import Bucket, Prompt, AiModels
import os
from pdf_to_text_utility import PDFToTextUtilityManager

BASE_PDF_PATH = config('BASE_PDF_PATH')



def generate_gemini_content(audio):
    try:
        vertex_model = AiModels.VERTEX_MODEL.value
        model = GenerativeModel(model_name=vertex_model)
        prompt = Prompt.TRANSCRIPT_PROMPT.value

        # generation_config = generative_models.GenerationConfig(temperature=0)
        # Safety config
        safety_config = [
            generative_models.SafetySetting(
                category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            generative_models.SafetySetting(
                category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            generative_models.SafetySetting(
                category=generative_models.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            generative_models.SafetySetting(
                category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            generative_models.SafetySetting(
                category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),

        ]

        response = model.generate_content(
            [
                Part.from_data(
                    audio,
                    mime_type="audio/mp3",
                ),
                prompt,
            ],
            safety_settings=safety_config
        )

        # print(response.text)
        # print(response)
        return response
    except Exception as err:
        print(f"Gemini error: {err}")


def common_process(class_id):
    db_ops = DBOperations()
    file_ops = FileOperations()
    gpt_manager = GPTManager()
    s3_manager = S3Manager()

    print("\n--------------------convert the mp4 file to mp3-----------------------------\n")
    file_ops.write_audio_file(class_id=class_id)
    result = file_ops.cut_audio_file(class_id=class_id)
    print("\n--------------------create entry in the transcription status table-----------------------------\n")
    db_ops.update_transcription_status(class_id=class_id, status=0)

    print("\n--------------------read and transcribe the audio file with gemini-----------------------------\n")
    for res in result:
        audio = file_ops.read_mp3_file(res)
        response = generate_gemini_content(audio)
        output_part = res.split(".")[0][-1]
        file_ops.write_cut_transcription_file(response.text, class_id, int(output_part))

    print("\n--------------------improve the transcription using gpt-----------------------------\n")
    gpt_manager.gpt_improve_transcript(class_id=class_id)
    print("\n--------------------add the synopsis-----------------------------\n")

    synopsis = db_ops.get_synopsis_from_db(class_id=class_id)
    file_name = f"{class_id}_gemini_transcript_improved.txt"

    file_ops.write_content_to_file(
        content=f"\n Synopsis: \n {synopsis}",
        class_id=class_id,
        file_name=file_name
    )

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

        print(f"--------converting the handout pdf to text for {class_id}----------------")
        utility_manager = PDFToTextUtilityManager(s3_pdf_file_path=f"classroom/handouts/{handout_loc}")
        handout_content = utility_manager.pdf_processing()
        print(f"--------writing content to transcript file for {class_id}----------------")
        file_ops.write_content_to_file(
            content=f"\n Class Notes: \n {handout_content}",
            class_id=class_id,
            file_name=file_name
        )

    print("\n--------------------load and split the content from the transcript-----------------------------\n")

    pages = file_ops.load_text_file(class_id=class_id)
    print(f"splitting transcription file {class_id}.....")
    docs = recursive_text_splitter(pages)
    print(f"embedding splits {class_id}.....")
    db_ops = DBOperations()
    section = db_ops.get_section_id(class_id=class_id)
    if embed_data(docs, section=section, class_id=class_id):
        print(f"\n-----------------updating transcription status in db for {class_id}---------------------\n")
        db_ops.update_transcription_status(class_id=class_id, status=1)
        print(f"\n-----------------uploading files on s3 for {class_id}---------------------\n")
        s3_manager.upload_transcript_subtitle_to_s3(class_id=class_id, bucket=Bucket.RESOURCES_BUCKET.value)
        print(f"\n-----------------deleting files from local for {class_id}---------------------\n")
        file_ops.delete_files_from_local(class_id=class_id)
        print(f"\n-----------------transcription for the video {class_id} completed.---------------------\n")


def gcp_process(class_id):

    db_ops = DBOperations()
    embed_code_id = db_ops.get_id_from_embed_code(class_id=class_id)
    signed_url = get_signed_url(embed_code_id=embed_code_id)

    if not signed_url:
        print("No videos exist on GCP for the given class id")
    else:
        print("\n--------------------download video file from gcp to local-----------------------------\n")
        if download_file_from_gcp(class_id=class_id, signed_url=signed_url):
            common_process(class_id=class_id)
        else:
            print(f"Video with lecture id {class_id} could not be downloaded")


def vdo_cipher_process(class_id):
    # Specify the path to your Excel file
    vdo_cipher_link_file = 'class_embed_code_link.xlsx'
    # Read the Excel file
    df = pd.read_excel(vdo_cipher_link_file)
    # Convert each row to a list
    rows_as_lists = df.values.tolist()
    class_id_url_dict = {}
    for row in rows_as_lists:
        class_id_url_dict[row[0]] = row[3]
    # print(class_id_url_dict)
    url = class_id_url_dict[int(class_id)]
    download_file_from_s3_using_excel((class_id, url))
    common_process(class_id=class_id)


if __name__ == "__main__":
    # List of class_ids for the videos to transcribe
    class_ids = sys.argv[1:]

    # Create a multiprocessing pool
    with multiprocessing.Pool() as pool:        # Map the transcribe_video function to each class_id in the pool
        pool.map(vdo_cipher_process, class_ids)

