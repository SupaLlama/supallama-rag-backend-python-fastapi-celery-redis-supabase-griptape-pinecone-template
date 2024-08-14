import logging

from celery import shared_task

from griptape.drivers import OpenAiEmbeddingDriver, PineconeVectorStoreDriver
from griptape.loaders import WebLoader

from app.config import settings


logging.basicConfig(level=logging.INFO)


# Define as shared_task instead of celery.task 
# to avoid circular imports, and allow this 
# file to work as expected anywhere in the app.
@shared_task
def crawl_url_and_index_task(url: str, crawled_urls_id) -> None:
    """
    Crawl the URL and update its record's status in the 
    Supabase crawled_urls table.
    """    

    logging.debug("******** crawl_url_and_index_task ********")

    # Uncomment the 2 lines below to debug
    # this celery task via rdb over telnet!
    #
    # from celery.contrib import rdb
    # rdb.set_trace()

    if url is None or type(url) is not str or len(url) == 0:
        logging.error("Invalid URL")
        return 
    
    if crawled_urls_id is None or type(crawled_urls_id) is not int or crawled_urls_id < 1:
        logging.error("Invalid crawled_urls_id")
        return
    

    logging.debug(f"Scraping Web Content from: {url}")
    artifacts = WebLoader().load(url)

    logging.debug("Embedding Text Artifacts and Adding to Pinecone Index")
    vector_store_driver = PineconeVectorStoreDriver(
        api_key=settings.PINECONE_API_KEY,
        environment="",
        index_name=settings.PINECONE_INDEX_NAME,
        embedding_driver=OpenAiEmbeddingDriver(),
    )    

    namespace = "web-content"
    logging.debug(f"Using vector store namespace: {namespace}")

    vector_store_driver.upsert_text_artifacts(
        {namespace: artifacts}
    )

    logging.debug(f"Successfully Crawled & Indexed URL: {url}")
