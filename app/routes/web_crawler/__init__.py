from fastapi import APIRouter


web_crawler_router = APIRouter(
    prefix="/web-crawler",
)

# Import items from current directory at the end of
# this file since endpoints.py imports llm_router
# from this module initializer.
from . import endpoints, schemas, tasks # noqa
