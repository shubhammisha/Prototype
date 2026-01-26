from fastembed import TextEmbedding
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_name = "BAAI/bge-small-en-v1.5"
logger.info(f"Start downloading model: {model_name}...")

try:
    model = TextEmbedding(model_name=model_name)
    logger.info("Model download and load successful!")
    # Test embedding
    embeddings = list(model.embed(["Hello world"]))
    if len(embeddings) > 0:
        logger.info(f"Embedding test passed. Shape: {embeddings[0].shape}")
except Exception as e:
    logger.error(f"Failed to download model: {e}")
    raise e
