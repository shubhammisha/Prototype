from pydantic import BaseModel

class HealthCheck(BaseModel):
    status: str = "ok"

class ErrorResponse(BaseModel):
    detail: str
