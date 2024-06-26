import sys
import multiprocessing
from gemini_process_transcript import process


def transcribe_video(class_id):
    process(class_id=class_id)


if __name__ == "__main__":
    # List of class_ids for the videos to transcribe
    class_ids = sys.argv[1:]

    # Create a multiprocessing pool
    with multiprocessing.Pool() as pool:        # Map the transcribe_video function to each class_id in the pool
        pool.map(transcribe_video, class_ids)
