from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat import ChatRequest, ChatResponse, SourceSnippet
from app.services.rag import RAGService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get service (could be singleton)
def get_rag_service():
    return RAGService()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service)
):
    try:
        logger.info(f"Chat request: {request.query} with filters: {request.filters}")
        result = service.generate_response(request.query, filters=request.filters)
        
        answer = result["answer"]
        chunks = result["sources"]
        
        sources = []
        for chunk in chunks:
            sources.append(SourceSnippet(
                text=chunk.text[:200] + "...", # Truncate for snippet
                source=chunk.metadata.get("source", "Unknown"),
                page=chunk.metadata.get("page", 0)
            ))
            
        # Basic confidence logic
        confidence = "High" if chunks else "Low"
        if "I don't know" in answer:
            confidence = "Low"
            
        return ChatResponse(
            answer=answer,
            sources=sources,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
