import boto3
from decouple import config

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY_ID = config('AWS_SECRET_KEY_ID')

BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
# BASE_SUBTITLE_PATH = config('BASE_SUBTITLE_PATH')
S3_BUCKET = config('S3_BUCKET')


def upload_transcript_subtitle_to_s3(class_id):
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_KEY_ID
                             )
    try:
        transcript_file_name = f"{class_id}_gemini_transcript.txt"
        # subtitle_file_name = f"{class_id}_sub.srt"
        improved_transcript_file_name = f"{class_id}_gemini_transcript_improved.txt"
        local_transcript_file_path = f"{BASE_TRANSCRIPT_PATH}{class_id}/{transcript_file_name}"
        # local_subtitle_file_path = f"{BASE_SUBTITLE_PATH}/{subtitle_file_name}"
        s3_client.upload_file(local_transcript_file_path, S3_BUCKET, f"ai_live_query_resolution/gemini_transcripts/{transcript_file_name}")
        s3_client.upload_file(local_transcript_file_path, S3_BUCKET, f"ai_live_query_resolution/gemini_improved_transcripts/{improved_transcript_file_name}")
        # s3_client.upload_file(local_subtitle_file_path, S3_BUCKET, f"ai_live_query_resolution/subtitles/{subtitle_file_name}")
    except Exception as err:
        print(err)
