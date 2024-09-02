from enum import Enum

class Prompt(Enum):
    IMAGE_TO_TEXT_PROMPT = """
    Act as an OCR and extract all the text context from the image.
    If there are any pictures then explain them in brief.
    Do not narrate and exclude the footer. 
    
    """

    TRANSCRIPT_IMPROVEMENT_PROMPT = """
    Act as a translator and convert all hinglish statements into english only statements and fix all grammar mistakes of the
    given content and keep the structure of the content same as it is and consistent without reformatting
    """

    TRANSCRIPT_PROMPT = '''
    <instructions>
    You are given an audio file. It contains a lecture.
    It can be in any hindi or english or in both. 
    1. Use only english to write the transcription.
    2. Follow proper punctuation in the conversation and never miss/misspell or add any word/text during the transcription.
    3. Don't mention the time in the transcription. only output the texts.
    </instructions>
    '''


class Bucket(Enum):
    RESOURCES_BUCKET = "visionresources"
    ASSETS_BUCKET = "visionassets"


class AiModels(Enum):
    GPT_AUDIO_MODEL = "whisper-1"
    VERTEX_MODEL = "gemini-1.5-pro-preview-0409"
    GPT_TEXT_MODEL = "gpt-4o"