import sys
import multiprocessing

from fetch_embed_code import get_id_from_embed_code
from download_video import (
    get_signed_url,
    download_file
)
from create_transcription import (
    write_audio_file,
    load_audio_file,
    decode_audio_file,
    write_transcription_file,
    write_srt_file
)

from process_transcript import (
    load_text_file,
    recursive_text_splitter,
    embed_data
)

from update_db import update_transcription_status
from delete_files import delete_files_from_local

from upload_on_s3 import upload_transcript_subtitle_to_s3


def transcribe_video(class_id):
    embed_code_id = get_id_from_embed_code(class_id=class_id)
    signed_url = get_signed_url(embed_code_id=embed_code_id)
    if not signed_url:
        print("No videos exist on GCP for the given class id")
    else:
        print(f"Transcribing video {class_id}...")
        if download_file(signed_url=signed_url, class_id=class_id):
            write_audio_file(class_id=class_id)
            audio = load_audio_file(class_id=class_id)
            print(f"decoding audio file for {class_id}.....")
            transcript = decode_audio_file(audio=audio)
            print(f"writing transcription file for.....{class_id}")
            write_transcription_file(transcript_text=transcript['text'], class_id=class_id)
            write_srt_file(transcript=transcript, class_id=class_id)
            print(f"loading transcription file {class_id}.....")
            pages = load_text_file(class_id=class_id)
            print(f"splitting transcription file {class_id}.....")
            docs = recursive_text_splitter(pages)
            print(f"embedding splits {class_id}.....")
            if embed_data(docs):
                print(f"updating transcription status in db for {class_id}.....")
                update_transcription_status(class_id=class_id)
                print(f"uploading transcription and subtitle files to s3 for {class_id}.....")
                upload_transcript_subtitle_to_s3(class_id=class_id)
                print(f"deleting files from local memory for {class_id}..............")
                delete_files_from_local(class_id=class_id)
                print(f"Transcription for video {class_id} complete.")


if __name__ == "__main__":
    # List of class_ids for the videos to transcribe
    class_ids = sys.argv[1:]

    # Create a multiprocessing pool
    with multiprocessing.Pool() as pool:        # Map the transcribe_video function to each class_id in the pool
        pool.map(transcribe_video, class_ids)
