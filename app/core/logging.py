import logging
import sys
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
