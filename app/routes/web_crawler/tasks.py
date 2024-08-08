from celery import shared_task

from langchain_community.document_loaders import FireCrawlLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import MarkdownTextSplitter

from app.config import settings


@shared_task
def crawl_url_and_index_task(url: str) -> str:
    """Define as shared_task instead of celery.task 
    to avoid circular imports, and allow this 
    file to work as expected anywhere in the app."""

    # Uncomment the 2 lines below to debug
    # this celery task via rdb over telnet!
    #
    # from celery.contrib import rdb
    # rdb.set_trace()

    print("******** crawl_url_and_index_task ********")
    print(f"firecrawl api key: {settings.FIRECRAWL_API_KEY}")
    print(f"pinecone index name: {settings.PINECONE_INDEX_NAME}")

    print(f"Crawling URL to index: {url}")
    loader = FireCrawlLoader(
        api_key=settings.FIRECRAWL_API_KEY,
        mode="scrape",
        url=url
    )
    docs = loader.load()

    print("Splitting markdown text")
    text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=20)
    split_docs = text_splitter.split_documents(docs)

    print("Embedding Split Documents and Adding to Pinecone Index")
    embeddings = OpenAIEmbeddings()
    PineconeVectorStore.from_documents(
        split_docs,
        embedding=embeddings,
        index_name=settings.PINECONE_INDEX_NAME
    ) 

    return f"Successfully Crawled & Indexed URL: {url}"