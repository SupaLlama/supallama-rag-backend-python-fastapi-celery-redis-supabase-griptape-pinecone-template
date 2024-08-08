from fastapi import APIRouter


llm_router = APIRouter(
    prefix="/llm",
)

# Import items from current directory at the end of
# this file since endpoints.py imports llm_router
# from this module initializer.
from . import endpoints, schemas, tasks # noqa
