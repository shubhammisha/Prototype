from typing import Optional, Union
from pydantic import BaseModel

class DocumentIngestRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class Document(BaseModel):
    text: str
    metadata: dict = {}

class DocumentResponse(BaseModel):
    id: str
    message: str

