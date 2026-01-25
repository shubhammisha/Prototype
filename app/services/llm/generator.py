from abc import ABC, abstractmethod
from groq import Groq
from app.core.config import settings

class BaseLLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response for the given prompt.
        """
        pass

class GroqLLMService(BaseLLMService):
    def __init__(self, api_key: str = settings.GROQ_API_KEY, model: str = settings.LLM_MODEL):
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            # Helpful error logging
            print(f"Error calling Groq API with model {self.model}: {e}")
            raise e

def get_llm_service() -> BaseLLMService:
    return GroqLLMService()
