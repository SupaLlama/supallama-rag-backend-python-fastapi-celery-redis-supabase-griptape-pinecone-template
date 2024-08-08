from pydantic import BaseModel


class QueryPineconeIndexBody(BaseModel):

    question: str
