from typing import List
from app.core.prompts import STRICT_RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from app.services.retrieval import RetrievalService
from app.services.llm.generator import get_llm_service
from app.schemas.vector import VectorEmbedding

class RAGService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_service = get_llm_service()

    def format_context(self, chunks: List[VectorEmbedding]) -> str:
        """
        Format retrieved chunks into a context string with metadata citations.
        Format: "Content... [Source: DocName, Page: X]"
        """
        formatted_chunks = []
        for chunk in chunks:
            source = chunk.metadata.get("source", "Unknown")
            page = chunk.metadata.get("page", "Unknown")
            # Clean newline characters in text for cleaner context block
            clean_text = chunk.text.replace("\n", " ").strip()
            formatted_chunks.append(f"{clean_text} [Source: {source}, Page: {page}]")
            
        return "\n\n".join(formatted_chunks)

    def generate_answer(self, query: str, chunks: List[VectorEmbedding]) -> str:
        """
        Generate a strict answer using the provided chunks.
        """
        if not chunks:
            return "I don't know based on the provided documents."

        # Format context
        context_str = self.format_context(chunks)

        # Construct Prompt
        prompt = RAG_USER_PROMPT_TEMPLATE.format(
            context=context_str,
            question=query
        )
        
        # Combine System + User Prompt
        full_prompt = f"{STRICT_RAG_SYSTEM_PROMPT}\n\n{prompt}"
        
        return self.llm_service.generate(full_prompt)

    def generate_response(self, query: str) -> dict:
        """
        Orchestrate the RAG flow: Retrieve -> Generate.
        Returns:
            dict: {
                "answer": str,
                "sources": List[VectorEmbedding]
            }
        """
        # 1. Retrieve relevant chunks
        chunks = self.retrieval_service.search(query, limit=5)
        
        # 2. Generate Answer
        answer = self.generate_answer(query, chunks)
        
        return {
            "answer": answer,
            "sources": chunks
        }


