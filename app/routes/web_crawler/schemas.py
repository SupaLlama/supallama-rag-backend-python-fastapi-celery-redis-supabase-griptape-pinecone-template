from pydantic import BaseModel


class CrawlUrlAndIndexBody(BaseModel):

    access_token: str
    url: str
