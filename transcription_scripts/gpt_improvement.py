from decouple import config
from openai import OpenAI
from file_operations import FileOperations

BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
BASE_CUT_TRANSCRIPT_FOLDER_PATH = config('BASE_CUT_TRANSCRIPT_FOLDER_PATH')
OPEN_AI_API_KEY = config('OPEN_AI_API_KEY')

PROMPT = """
Act as a translator and convert all hinglish statements into english only statements and fix all grammar mistakes of the
given content and keep the structure of the content same as it is and consistent without reformatting
"""


def gpt_api(class_id, prompt=PROMPT):
    file_ops = FileOperations()
    client = OpenAI(api_key=OPEN_AI_API_KEY)
    directory_path = f"{BASE_CUT_TRANSCRIPT_FOLDER_PATH}{class_id}/"
    files = file_ops.list_files_in_directory(directory_path)

    for file in files:
        print(f"improving the file {file}.......")
        content = file_ops.read_file(f"{directory_path}/{file}")
        # print(content)
        completion = client.chat.completions.create(
          model="gpt-4o",
          temperature=0.1,
          messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{content}"}
          ]
        )
        improved_content = completion.choices[0].message.content
        file_name = f"{class_id}_gemini_transcript_improved.txt"
        file_ops.write_transcript_to_file(
            content=improved_content,
            class_id=class_id,
            file_name=file_name
        )
        file_name = f"{class_id}_gemini_transcript.txt"
        file_ops.write_transcript_to_file(
            content=content,
            class_id=class_id,
            file_name=file_name
        )
