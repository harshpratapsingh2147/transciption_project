from langchain.embeddings.openai import OpenAIEmbeddings


class CustomOpenAIEmbeddings(OpenAIEmbeddings):

    def __init__(self, openai_api_key, model='text-embedding-3-large', *args, **kwargs):
        super().__init__(openai_api_key=openai_api_key, model=model, *args, **kwargs)

    def _embed_documents(self, texts):
        return super().embed_documents(texts)

    def __call__(self, input):
        return self._embed_documents(input)