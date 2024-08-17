import logging

from fastapi.responses import JSONResponse

from app.jwt_utils import verify_jwt
from app.supabase_utils import (
    get_user_from_supabase_auth, 
    insert_new_record_in_crawled_urls_table
)

from . import web_crawler_router
from .schemas import CrawlUrlAndIndexBody
from .tasks import crawl_url_and_index_task


# Logging Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web-crawler-endpoints") 


@web_crawler_router.post("/crawl-url-and-index")
def crawl_url_and_index(request_body: CrawlUrlAndIndexBody) -> JSONResponse:
    """
    Crawl the URL, index the contents in a vector store
    and update the Supabase crawled_urls table.
    """
    logger.info("In crawl_url_and_index router handler")
    
    if request_body.access_token is None or type(request_body.access_token) is not str:
        logger.error(f"Invalid JWT: {request_body.access_token}")
        return JSONResponse({"error": "Invalid JWT"})

    if request_body.url is None or type(request_body.url) is not str:
        logger.error(f"Invalid URL: {request_body.url}")
        return JSONResponse({"error": "Invalid URL"})

    logger.info("Verify the JWT using the JWT Secret and 'authenticated' audience")
    if not verify_jwt(request_body.access_token, 'authenticated'):
        logger.error(f"Unable to verify JWT: {request_body.access_token}")
        return JSONResponse({"error": "Unable to verify JWT"})

    logger.info("Get the user from the Supabase Auth database to double-check the JWT")
    user_id = get_user_from_supabase_auth(request_body.access_token)

    if user_id is None:
        logger.error("Will not crawl URL since user is not logged in")
        return JSONResponse({"error": "User is not logged in"})

    logger.info("Inserting new record in the Supabase crawled_urls table")
    new_crawled_urls_record = insert_new_record_in_crawled_urls_table(
        user_id, request_body.url
    ) 

    logger.info(new_crawled_urls_record)

    if len(new_crawled_urls_record) != 1:
        logger.error("Did not insert single record into crawled_urls table")
        return JSONResponse({"error": "Error accessing URL cralwer database"})

    new_crawled_urls_record_id = new_crawled_urls_record[0]["id"]

    # Offload the url crawling task to Celery
    task = crawl_url_and_index_task.delay(request_body.url, new_crawled_urls_record_id, user_id)

    # Return the Celery Task ID which can be
    # used to check on the Task's status.
    return JSONResponse({"task_id": task.task_id})
