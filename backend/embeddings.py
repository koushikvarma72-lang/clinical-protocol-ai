import requests
import traceback

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"   # ✅ change if needed


def get_embedding(text: str):
    """
    Sends text to Ollama and gets vector embedding.
    """
    try:
        if not text or not text.strip():
            raise Exception("Empty text provided for embedding")
            
        prompt_text = f"search_query: {text.strip()}"

        payload = {
            "model": EMBED_MODEL,
            "prompt": prompt_text 
        }

        print(f"Getting embedding from Ollama at {OLLAMA_URL}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)  # Increased to 2 minutes
        
        if response.status_code != 200:
            raise Exception(f"Ollama HTTP error {response.status_code}: {response.text}")
        
        data = response.json()

        if "embedding" in data:
            embedding = data["embedding"]
            if not embedding or len(embedding) == 0:
                raise Exception("Ollama returned empty embedding")
            return embedding

        raise Exception(f"Ollama embedding error - no 'embedding' key in response: {data}")
        
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Please make sure Ollama is running on localhost:11434")
    except requests.exceptions.Timeout:
        raise Exception("Ollama embedding request timed out. The model might be loading.")
    except Exception as e:
        print(f"Embedding error details: {str(e)}")
        raise Exception(f"Error getting embedding: {str(e)}")
