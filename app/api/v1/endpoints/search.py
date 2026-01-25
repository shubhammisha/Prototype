from fastapi import APIRouter

router = APIRouter()

@router.get("/vector/{query}")
async def search_vector(query: str):
    return {"results": [{"id": "1", "score": 0.9}]}
