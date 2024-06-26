import re
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from decouple import config
import uuid
from customEmbeddings import CustomOpenAIEmbeddings

BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
api_key = config('OPEN_AI_API_KEY')


def extract_id(embed_code):
    # Define a regular expression pattern to extract the ID
    pattern = r'id=([\w]+)'
    match = re.search(pattern, embed_code)

    if match:
        # Extract the ID from the matched group
        id_value = match.group(1)
        return id_value
    else:
        return None


def parse_synopsis(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()


def recursive_text_splitter(pages):
    chunk_size = 1500
    chunk_overlap = 100

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

        ids = []
        metadatas = []
        documents = []

        for doc in docs:
            ids.append(str(uuid.uuid1()))
            metadatas.append(doc.metadata)
            documents.append(doc.page_content)
        embedding = CustomOpenAIEmbeddings(openai_api_key=api_key)
        collection = client.get_or_create_collection(name="live_query", embedding_function=embedding)
        collection.add(
            ids=ids, metadatas=metadatas, documents=documents
        )

        return True
    except Exception as err:
        print("Here is the issue: ", err)
        return False
