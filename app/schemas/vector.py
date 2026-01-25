from pydantic import BaseModel, Field

class VectorEmbedding(BaseModel):
    """
    Represents a text chunk with its vector embedding and metadata.
    """
    text: str
    vector: list[float]
    metadata: dict = Field(default_factory=dict)
