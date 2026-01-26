
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    # Try the most likely model names
    models = ["nomic-embed-text-v1.5", "llama-3.1-8b-instant"]
    
    for model in models:
        print(f"Testing model: {model}")
        try:
            # Standard OpenAI-compatible API
            resp = client.embeddings.create(
                input="The food was delicious and the waiter...",
                model=model
            )
            print(f"Success! Vector length: {len(resp.data[0].embedding)}")
            break
        except Exception as e:
            print(f"Failed with {model}: {e}")
            
except Exception as e:
    print(f"Critical Error: {e}")
