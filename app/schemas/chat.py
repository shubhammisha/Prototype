from typing import Optional, Union, List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = None

class SourceSnippet(BaseModel):
    text: str
    source: str
    page: Union[int, str]

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceSnippet]
    confidence: str = "Medium"

