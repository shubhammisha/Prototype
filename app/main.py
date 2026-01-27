from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router
from app.services.vector.store import QdrantVectorStore
from app.services.vector.embeddings import get_embedding_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure vector collection exists
    try:
        store = QdrantVectorStore()
        # Default text-v1.5 is 768 dims. Ideally read from config or dynamic.
        # For now, hardcoding 768 as per previous plan to ensure it's set.
        store.ensure_collection(vector_size=384)
        print(f"Startup: Verified collection '{settings.VECTOR_COLLECTION_NAME}' exists.")
        
        # Pre-load embedding model
        print("Startup: Pre-loading embedding model...")
        get_embedding_service()
        print("Startup: Embedding model loaded.")
    except Exception as e:
        print(f"Startup Warning: Could not verify vector store: {e}")
    
    yield
    # Shutdown logic if needed

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/")
async def root():
    return {"message": "Welcome to RAG Backend API. Visit /docs for Swagger UI."}

