import whisper
from whisper.utils import get_writer
from moviepy.editor import *
from decouple import config
from fetch_synopsis import get_synopsis_from_db

BASE_DOWNLOAD_VIDEO_PATH = config('BASE_DOWNLOAD_VIDEO_PATH')
BASE_AUDIO_PATH = config('BASE_AUDIO_PATH')
BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
BASE_SUBTITLE_PATH = config('BASE_SUBTITLE_PATH')


def write_audio_file(class_id):
    # load video and extract audio from it
    video = VideoFileClip(f"{BASE_DOWNLOAD_VIDEO_PATH}{class_id}.mp4")
    video.audio.write_audiofile(f"{BASE_AUDIO_PATH}{class_id}.mp3")


def load_audio_file(class_id):
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(f"{BASE_AUDIO_PATH}{class_id}.mp3")
    return audio


def decode_audio_file(audio):
    model = whisper.load_model("medium.en")
    result = model.transcribe(audio)
    return result


def write_transcription_file(transcript_text, class_id):
    # Specify the file path where you want to save the text file
    text_file_path = f"{BASE_TRANSCRIPT_PATH}{class_id}_transcript.txt"
    synopsis = get_synopsis_from_db(class_id=class_id)
    final_transcript_text = transcript_text + "\n" + "Synopsis:" + synopsis
    # Write the transcription string to the text file
    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(final_transcript_text)


def write_srt_file(transcript, class_id):
    writer = get_writer("srt", str(BASE_SUBTITLE_PATH))
    writer(transcript, f"{class_id}_sub")
