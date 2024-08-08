from celery import shared_task

from griptape.drivers import OpenAiEmbeddingDriver, PineconeVectorStoreDriver
from griptape.loaders import WebLoader

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
    # print(f"firecrawl api key: {settings.FIRECRAWL_API_KEY}")
    print(f"pinecone index name: {settings.PINECONE_INDEX_NAME}")

    print(f"Scraping Web Content from: {url}")
    artifacts = WebLoader().load(url)

    print("Embedding Text Artifacts and Adding to Pinecone Index")
    vector_store_driver = PineconeVectorStoreDriver(
        api_key=settings.PINECONE_API_KEY,
        environment="",
        index_name=settings.PINECONE_INDEX_NAME,
        embedding_driver=OpenAiEmbeddingDriver(),
    )    

    namespace = "web-content"

    vector_store_driver.upsert_text_artifacts(
        {namespace: artifacts}
    )

    return f"Successfully Crawled & Indexed URL: {url}"