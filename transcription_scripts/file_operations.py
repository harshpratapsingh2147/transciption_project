import os
from moviepy.editor import *
from decouple import config
import shutil
from langchain.document_loaders import TextLoader


class FileOperations:

    def __init__(self):
        self.base_transcript_path = config('BASE_TRANSCRIPT_PATH')
        self.base_cut_transcript_path = config('BASE_CUT_TRANSCRIPT_FOLDER_PATH')
        self.base_download_video_path = config('BASE_DOWNLOAD_VIDEO_PATH')
        self.base_audio_path = config('BASE_AUDIO_PATH')
        self.base_cut_audio_folder_path = config('BASE_CUT_AUDIO_FOLDER_PATH')
        self.base_subtitle_path = config('BASE_SUBTITLE_PATH')

    def write_audio_file(self, class_id):
        # load video and extract audio from it
        video = VideoFileClip(f"{self.base_download_video_path}{class_id}.mp4")
        video.audio.write_audiofile(f"{self.base_audio_path}{class_id}.mp3")

    def cut_audio_file(self, class_id):
        cut_audio_folder_name = f"{self.base_cut_audio_folder_path}{class_id}"
        # if not os.path.exists(cut_folder_name):
        os.makedirs(cut_audio_folder_name, exist_ok=True)
        input_path = f"{self.base_audio_path}{class_id}.mp3"
        audio_clip = AudioFileClip(input_path)
        total_duration = audio_clip.duration
        print(total_duration)
        clip_duration = 20 * 60
        i = 0
        c = 0
        res = []
        while c <= total_duration:
            start_time = i * clip_duration
            end_time = ((i + 1) * clip_duration)
            if end_time > total_duration:
                end_time = total_duration
            extracted_audio = audio_clip.subclip(start_time, end_time)
            print("start and end time :", start_time, end_time)
            i += 1
            c = i * clip_duration
            output_file_name = f"{class_id}_part_{i}.mp3"
            extracted_audio.write_audiofile(f"{cut_audio_folder_name}/{output_file_name}")
            res.append(f"{cut_audio_folder_name}/{output_file_name}")

        audio_clip.close()
        return res

    def read_mp3_file(self, filename):
        with open(filename, 'rb') as file:
            mp3_bytes = file.read()
            # print(mp3_bytes)
        return mp3_bytes

    def write_cut_transcription_file(self, response, class_id, part=1):
        # res = [*response]
        output_folder = f"{self.base_cut_transcript_path}{class_id}/"
        os.makedirs(output_folder, exist_ok=True)
        with open(output_folder + f"{class_id}_part_{part}.txt", "w") as file:
            file.write(response)

    def list_files_in_directory(self, directory_path):
        # Get a list of all items in the directory
        items = os.listdir(directory_path)

        # Filter out only the files
        files = sorted([item for item in items if os.path.isfile(os.path.join(directory_path, item))])
        print(files)
        return files

    def write_transcript_to_file(self, content, class_id, file_name):
        output_folder = f"{self.base_transcript_path}{class_id}/"
        os.makedirs(output_folder, exist_ok=True)
        with open(output_folder + f"{file_name}", "a") as file:
            file.write(content)

    # def write_srt_file(self, transcript, class_id):
    #     writer = get_writer("srt", str(BASE_SUBTITLE_PATH))
    #     writer(transcript, f"{class_id}_sub")

    def delete_files_from_local(self, class_id):
        os.remove(f"{self.base_download_video_path}{class_id}.mp4")
        os.remove(f"{self.base_audio_path}{class_id}.mp3")
        # os.remove(f"{self.base_subtitle_path}{class_id}_sub.srt")
        shutil.rmtree(f"{self.base_transcript_path}{class_id}")
        shutil.rmtree(f"{self.base_cut_transcript_path}{class_id}")

    def read_file(self, file_path):
        with open(file_path, "r") as file:
            return file.read()

    def load_text_file(self, class_id):
        loader = TextLoader(f"{self.base_transcript_path}{class_id}/{class_id}_gemini_transcript_improved.txt")
        pages = loader.load()
        return pages