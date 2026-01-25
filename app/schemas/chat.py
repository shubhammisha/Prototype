from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    history: list[dict] | None = None

class SourceSnippet(BaseModel):
    text: str
    source: str
    page: int | str

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
    confidence: str = "Medium"

