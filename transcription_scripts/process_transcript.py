from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from decouple import config
import chromadb
# from chromadb

BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')

api_key = config('OPEN_AI_API_KEY')


def load_text_file(class_id):
    loader = TextLoader(f"{BASE_TRANSCRIPT_PATH}{class_id}_transcript.txt")
    pages = loader.load()
    return pages


def recursive_text_splitter(pages):
    chunk_size = 500
    chunk_overlap = 4

    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    docs = r_splitter.split_documents(pages)
    # print(docs)
    return docs


def embed_data(docs):
    try:
        client = chromadb.HttpClient(host='localhost', port=8000)
        embedding = OpenAIEmbeddings(api_key=api_key)
        vectordb = Chroma.from_documents(
            client=client,
            documents=docs,
            embedding=embedding,
        )
        return True
    except Exception as err:
        print("Here is the issue: ", err)
        return False
