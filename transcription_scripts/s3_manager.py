import boto3
from decouple import config


class S3Manager:

    def __init__(self):
        self.aws_access_key_id = config('AWS_ACCESS_KEY_ID')
        self.aws_secret_key_id = config('AWS_SECRET_KEY_ID')
        self.base_transcript_path = config('BASE_TRANSCRIPT_PATH')
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=self.aws_access_key_id,
                                      aws_secret_access_key=self.aws_secret_key_id
                                      )

    def upload_transcript_subtitle_to_s3(self, class_id, bucket, gpt_transcription=False):
        try:
            transcript_file_name = f"{class_id}_gemini_transcript.txt"
            improved_transcript_file_name = f"{class_id}_gemini_transcript_improved.txt"
            improved_local_transcript_file_path = f"{self.base_transcript_path}{class_id}/{improved_transcript_file_name}"
            if not gpt_transcription:
                local_transcript_file_path = f"{self.base_transcript_path}{class_id}/{transcript_file_name}"
                self.s3_client.upload_file(local_transcript_file_path, bucket,
                                           f"ai_live_query_resolution/gemini_transcripts/{transcript_file_name}")
            self.s3_client.upload_file(improved_local_transcript_file_path, bucket,
                                       f"ai_live_query_resolution/gemini_improved_transcripts/{improved_transcript_file_name}")

        except Exception as err:
            print(err)

    def download_file_from_s3(self, key, download_path, bucket):
        """ S3 File download"""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)

            with open(download_path, "wb") as f:
                for chunk in response['Body'].iter_chunks():
                    f.write(chunk)

            print(f"File downloaded successfully: {download_path}")

        except Exception as e:
            print(f"Error: {e}")

    def get_all_objects(self, prefix, bucket):
        try:
            response = self.s3_client.list_objects(
                Bucket=bucket,
                Prefix=prefix
            )

            list_of_file_path = [obj['Key'] for obj in response.get('Contents', [])]
            return list_of_file_path
        except Exception as e:
            print(f"Error: {e}")


    def upload_file_on_s3(self, s3_upload_path: str, local_file_path: str, bucket) -> None:
        """S3 File upload"""
        try:
            response = self.s3_client.upload_file(local_file_path, bucket, s3_upload_path)
        except Exception as e:
            print(f"Error: {e}")




