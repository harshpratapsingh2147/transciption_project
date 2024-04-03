import sys
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

class_id = sys.argv[1]
embed_code_id = get_id_from_embed_code(class_id=class_id)
signed_url = get_signed_url(embed_code_id=embed_code_id)

if not signed_url:
    print("No videos exist on GCP for the given class id")
else:
    download_file(signed_url=signed_url, class_id=class_id)
    write_audio_file(class_id=class_id)
    print("loading audio file.....")
    audio = load_audio_file(class_id=class_id)
    print("decoding audio file.....")
    transcript = decode_audio_file(audio=audio)
    print("writing transcription file.....")
    write_transcription_file(transcript_text=transcript['text'], class_id=class_id)
    print("writing srt file.....")
    write_srt_file(transcript=transcript, class_id=class_id)
    print("loading transcription file.....")
    pages = load_text_file(class_id=class_id)
    print("splitting transcription file.....")
    docs = recursive_text_splitter(pages)
    print("embedding splits.....")
    db = embed_data(docs)
    print("updating transcription status in db.....")
    update_transcription_status(class_id=class_id)
    print("uploading transcription and subtitle files to s3.....")
    upload_transcript_subtitle_to_s3(class_id=class_id)
    print("deleting files from local memory..............")
    delete_files_from_local(class_id=class_id)
