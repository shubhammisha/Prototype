from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.schemas.document import DocumentResponse
from app.services.document.loader import PDFLoader
from app.services.document.chunker import DocumentChunker
from app.services.retrieval import RetrievalService
from app.core.config import settings
import shutil
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependencies
def get_retrieval_service():
    return RetrievalService()

def get_loader():
    return PDFLoader()

def get_chunker():
    return DocumentChunker()

@router.post("/ingest", response_model=DocumentResponse)
async def ingest_document(
    file: UploadFile = File(...),
    loader: PDFLoader = Depends(get_loader),
    chunker: DocumentChunker = Depends(get_chunker),
    retrieval: RetrievalService = Depends(get_retrieval_service)
):
    try:
        # 1. Save temp file
        file_location = settings.UPLOAD_DIR / file.filename
        file_location.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Saved file to {file_location}")

        # 2. Load Documents (Text + Metadata)
        documents = loader.load(file_location)
        if not documents:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # 3. Chunk Documents
        chunks = chunker.chunk(documents)
        logger.info(f"Created {len(chunks)} chunks from {file.filename}")

        # 4. Index Chunks
        texts = [chunk.text for chunk in chunks]
        metas = [chunk.metadata for chunk in chunks]
        
        retrieval.index_documents(texts, metas)
        
        return DocumentResponse(
            id=file.filename,
            message=f"Successfully ingested {len(chunks)} chunks from {file.filename}"
        )

    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file? Optional. Keeping for debug for now.
        pass

