from vertexai.generative_models import GenerativeModel, Part
from vertexai import generative_models
from moviepy.editor import *
from db_operations import DBOperations
from download_video import *
from gpt_improvement import *
from utility import *
from file_operations import FileOperations
from s3_manager import *


def generate_gemini_content(audio):
    try:
        vertex_model = "gemini-1.5-pro-preview-0409"
        model = GenerativeModel(model_name=vertex_model)
        prompt = '''
                <instructions>
                You are given an audio file. It contains a lecture.
                It can be in any hindi or english or in both. 
                1. Use only english to write the transcription.
                2. Follow proper punctuation in the conversation and never miss/misspell or add any word/text during the transcription.
                3. Don't mention the time in the transcription. only output the texts.
                </instructions>
            '''

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


def process(class_id):

    db_ops = DBOperations()
    # embed_code_id = db_ops.get_id_from_embed_code(class_id=class_id)
    # signed_url = get_signed_url(embed_code_id=embed_code_id)

    # if not signed_url:
    if not True:
        print("No videos exist on GCP for the given class id")
    else:
        file_ops = FileOperations()

        # print("\n--------------------download video file from gcp to local-----------------------------\n")
        # if download_file(class_id=class_id, signed_url=signed_url):
        if True:

            print("\n--------------------convert the mp4 file to mp3-----------------------------\n")
            file_ops = FileOperations()
            file_ops.write_audio_file(class_id=class_id)
            result = file_ops.cut_audio_file(class_id=class_id)
            print("\n--------------------read and transcribe the audio file with gemini-----------------------------\n")

            for res in result:
                audio = file_ops.read_mp3_file(res)
                response = generate_gemini_content(audio)
                output_part = res.split(".")[0][-1]
                file_ops.write_cut_transcription_file(response.text, class_id, int(output_part))

        print("\n--------------------improve the transcription using gpt-----------------------------\n")
        gpt_api(class_id=class_id)
        print("\n--------------------add the synopsis-----------------------------\n")

        synopsis = db_ops.get_synopsis_from_db(class_id=class_id)
        file_name = f"{class_id}_gemini_transcript_improved.txt"

        file_ops.write_transcript_to_file(
            content=f"\n Synopsis: \n {synopsis}",
            class_id=class_id,
            file_name=file_name
        )

        s3_manager = S3Manager()
        s3_manager.upload_transcript_subtitle_to_s3(class_id=class_id)
        print(f"\n-----------------deleting files from local for {class_id}---------------------\n")
        file_ops.delete_files_from_local(class_id=class_id)
        print(f"\n-----------------transcription for the video {class_id} completed.---------------------\n")

        # print("\n--------------------load and split the content from the transcript-----------------------------\n")
        #
        # pages = file_ops.load_text_file(class_id=class_id)
        # print(f"splitting transcription file {class_id}.....")
        # docs = recursive_text_splitter(pages)
        # print(f"embedding splits {class_id}.....")

        # if embed_data(docs):
        #     print(f"\n-----------------updating transcription status in db for {class_id}---------------------\n")
        #     db_ops.update_transcription_status(class_id=class_id)
        #     print(f"\n-----------------uploading files on s3 for {class_id}---------------------\n")
        #     s3_manager = S3Manager()
        #     s3_manager.upload_transcript_subtitle_to_s3(class_id=class_id)
        #     print(f"\n-----------------deleting files from local for {class_id}---------------------\n")
        #     file_ops.delete_files_from_local(class_id=class_id)
        #     print(f"\n-----------------transcription for the video {class_id} completed.---------------------\n")


