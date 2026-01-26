from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
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
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    loader: PDFLoader = Depends(get_loader),
    retrieval: RetrievalService = Depends(get_retrieval_service)
):
    try:
        # 1. Save temp file synchronously (fast)
        file_location = settings.UPLOAD_DIR / file.filename
        file_location.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Saved file to {file_location}")

        # 2. Add heavy processing to background task
        background_tasks.add_task(
            process_upload_background, 
            file_path=file_location, 
            filename=file.filename,
            loader=loader, 
            retrieval=retrieval
        )
        
        return DocumentResponse(
            id=file.filename,
            message=f"File {file.filename} received. Processing started in background (this may take a minute for large files)."
        )

    except Exception as e:
        logger.error(f"Ingestion setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def process_upload_background(file_path: str, filename: str, loader: PDFLoader, retrieval: RetrievalService):
    """
    Heavy lifting function to be run in background.
    """
    try:
        logger.info(f"Background: Starting processing for {filename}...")
        
        # 2. Load Documents
        documents = loader.load(file_path)
        if not documents:
            logger.error(f"Background: Could not extract text from {filename}")
            return

        # 3. Index Documents
        texts = [doc.text for doc in documents]
        metas = [doc.metadata for doc in documents]
        
        retrieval.index_documents(texts, metas)
        
        logger.info(f"Background: Successfully finished processing {filename}")
        
    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {e}")
    finally:
        # Optional cleanup
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        pass

