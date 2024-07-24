from decouple import config
from openai import OpenAI
from file_operations import FileOperations
import os
from s3_manager import S3Manager
from db_operations import DBOperations
from utility import embed_data, recursive_text_splitter
import sys

BASE_CUT_AUDIO_FOLDER_PATH = config('BASE_CUT_AUDIO_FOLDER_PATH')
BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
BASE_CUT_TRANSCRIPT_FOLDER_PATH = config('BASE_CUT_TRANSCRIPT_FOLDER_PATH')
OPEN_AI_API_KEY = config('OPEN_AI_API_KEY')
GPT_AUDIO_MODEL = config('GPT_AUDIO_MODEL')
GPT_TEXT_MODEL = config('GPT_TEXT_MODEL')
PROMPT = """
Act as a translator and convert all hinglish statements into english only statements and fix all grammar mistakes of the
given content and keep the structure of the content same as it is and consistent without reformatting
"""


def gpt_improve_transcript(class_id, prompt=PROMPT):
    try:
        file_ops = FileOperations()
        client = OpenAI(api_key=OPEN_AI_API_KEY)
        directory_path = f"{BASE_CUT_TRANSCRIPT_FOLDER_PATH}{class_id}/"
        files = file_ops.list_files_in_directory(directory_path)

        for file in files:
            print(f"improving the file {file}.......")
            content = file_ops.read_file(f"{directory_path}/{file}")
            # print(content)
            completion = client.chat.completions.create(
              model=GPT_TEXT_MODEL,
              temperature=0.1,
              messages=[
                {"role": "system", "content": f"{prompt}"},
                {"role": "user", "content": f"{content}"}
              ]
            )
            improved_content = completion.choices[0].message.content
            file_name = f"{class_id}_gemini_transcript_improved.txt"
            file_ops.write_transcript_to_file(
                content=improved_content,
                class_id=class_id,
                file_name=file_name
            )
            file_name = f"{class_id}_gemini_transcript.txt"
            file_ops.write_transcript_to_file(
                content=content,
                class_id=class_id,
                file_name=file_name
            )
        return True
    except Exception as err:
        print(f"error in gpt api: {err}")
        return False


def gpt_transcribe_audio(class_id):
    # Set the API key
    client = OpenAI(api_key=OPEN_AI_API_KEY)
    file_ops = FileOperations()
    db_ops = DBOperations()
    file_name = f"{class_id}_gemini_transcript_improved.txt"

    # Transcribe the audio
    files = file_ops.list_files_in_directory(
        directory_path=f"{BASE_CUT_AUDIO_FOLDER_PATH}{class_id}/"
    )
    for file in files:
        print(file)
        transcription = client.audio.transcriptions.create(
            model=GPT_AUDIO_MODEL,
            file=open(f"{BASE_CUT_AUDIO_FOLDER_PATH}{class_id}/{file}", "rb"),
            language="en"
        )
        print(transcription)

        file_ops.write_transcript_to_file(
            content=transcription.text,
            class_id=class_id,
            file_name=file_name
        )

    synopsis = db_ops.get_synopsis_from_db(class_id=class_id)

    file_ops.write_transcript_to_file(
        content=f"\n Synopsis: \n {synopsis}",
        class_id=class_id,
        file_name=file_name
    )

    print("\n--------------------load and split the content from the transcript-----------------------------\n")

    pages = file_ops.load_text_file(class_id=class_id)
    print(f"splitting transcription file {class_id}.....")
    docs = recursive_text_splitter(pages)
    print(f"embedding splits {class_id}.....")
    if embed_data(docs):
        print(f"\n-----------------updating transcription status in db for {class_id}---------------------\n")
        db_ops.update_transcription_status(class_id=class_id)
        print(f"\n-----------------uploading files on s3 for {class_id}---------------------\n")
        s3_manager = S3Manager()
        s3_manager.upload_transcript_subtitle_to_s3(
            class_id=class_id,
            gpt_transcription=True
        )
        print(f"\n-----------------deleting files from local for {class_id}---------------------\n")
        file_ops.delete_files_from_local(
            class_id=class_id,
            gpt_transcription=True
        )
        print(f"\n-----------------transcription for the video {class_id} completed.---------------------\n")


if __name__ == "__main__":
    # List of class_ids for the videos to transcribe
    class_id = sys.argv[1:][0]
    gpt_transcribe_audio(class_id=class_id)
