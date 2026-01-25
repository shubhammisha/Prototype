from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

class RAGException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(RAGException)
    async def rag_exception_handler(request: Request, exc: RAGException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )
