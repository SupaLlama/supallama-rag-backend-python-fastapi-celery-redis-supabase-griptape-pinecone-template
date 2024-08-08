from fastapi.responses import JSONResponse

from . import web_crawler_router
from .schemas import CrawlUrlAndIndexBody
from .tasks import crawl_url_and_index_task

@web_crawler_router.post("/crawl-url-and-index")
def crawl_url_and_index(request_body: CrawlUrlAndIndexBody):
    # Offload the url crawling task to Celery
    task = crawl_url_and_index_task.delay(request_body.url)

    # Return the Celery Task ID which can be
    # used to check on the Task's status.
    return JSONResponse({"task_id": task.task_id})