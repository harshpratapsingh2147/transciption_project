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

class_id = sys.argv[1]
embed_code_id = get_id_from_embed_code(class_id=class_id)
signed_url = get_signed_url(embed_code_id=embed_code_id)
#
if not signed_url:
    print("No videos exist on GCP for the given class id")
else:
    download_file(signed_url=signed_url, class_id=class_id)
    write_audio_file(class_id=class_id)
    audio = load_audio_file(class_id=class_id)
    transcript = decode_audio_file(audio=audio)
    write_transcription_file(transcript_text=transcript['text'], class_id=class_id)
    write_srt_file(transcript=transcript, class_id=class_id)
    pages = load_text_file(class_id=class_id)
    docs = recursive_text_splitter(pages)
    db = embed_data(docs)
