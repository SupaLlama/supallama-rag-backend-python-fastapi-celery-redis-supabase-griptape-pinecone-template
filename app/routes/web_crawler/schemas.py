from pydantic import BaseModel


class CrawlUrlAndIndexBody(BaseModel):

    url: str
