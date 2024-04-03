import os
from decouple import config

BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
BASE_SUBTITLE_PATH = config('BASE_SUBTITLE_PATH')
BASE_VIDEO_PATH = config('BASE_DOWNLOAD_VIDEO_PATH')
BASE_AUDIO_PATH = config('BASE_AUDIO_PATH')


def delete_files_from_local(class_id):
    os.remove(f"{BASE_VIDEO_PATH}/{class_id}.mp4")
    os.remove(f"{BASE_AUDIO_PATH}/{class_id}.mp3")
    os.remove(f"{BASE_SUBTITLE_PATH}/{class_id}_sub.srt")
    os.remove(f"{BASE_TRANSCRIPT_PATH}/{class_id}_transcript.txt")
