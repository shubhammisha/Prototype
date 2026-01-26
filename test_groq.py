
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    # Try using a known embedding model or checking documentation behavior via trial
    # Nomic is often supported on Groq? Or maybe not.
    # Let's try to list models or just run a test.
    # Note: Groq mainly does LLM inference (Llama, Mixtral). 
    # They might not have an embeddings endpoint yet.
    # But let's check.
    
    print("Testing Groq...")
    # There is no client.embeddings.create in standard Groq python yet unless updated?
    # Let's check attributes
    if hasattr(client, 'embeddings'):
        print("Client has embeddings attribute!")
    else:
        print("Client DOES NOT have embeddings attribute.")
        
except Exception as e:ok
    print(f"Error: {e}")
