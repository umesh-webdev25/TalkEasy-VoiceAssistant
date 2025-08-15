from pydantic import BaseModel

class LLMQueryRequest(BaseModel):
    text: str
    max_tokens: int = 1000
    temperature: float = 0.7

class LLMQueryResponse(BaseModel):
    success: bool
    query: str
    response: str
    model: str
    usage: dict
