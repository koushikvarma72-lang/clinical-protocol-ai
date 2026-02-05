import requests
import traceback
import time

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"   # ✅ change if needed

# Cache for embeddings to avoid re-computing
_embedding_cache = {}

def get_embedding(text: str, timeout: int = 30, retries: int = 3):
    """
    Sends text to Ollama and gets vector embedding.
    Uses caching and retry logic to handle failures gracefully.
    """
    try:
        if not text or not text.strip():
            raise Exception("Empty text provided for embedding")
        
        # Check cache first
        text_hash = hash(text)
        if text_hash in _embedding_cache:
            return _embedding_cache[text_hash]
            
        prompt_text = f"search_query: {text.strip()}"

        payload = {
            "model": EMBED_MODEL,
            "prompt": prompt_text 
        }

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(retries):
            try:
                response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
                
                if response.status_code != 200:
                    last_error = f"Ollama HTTP error {response.status_code}: {response.text}"
                    if attempt < retries - 1:
                        time.sleep(1 * (attempt + 1))  # Exponential backoff
                        continue
                    raise Exception(last_error)
                
                data = response.json()

                if "embedding" in data:
                    embedding = data["embedding"]
                    if not embedding or len(embedding) == 0:
                        raise Exception("Ollama returned empty embedding")
                    
                    # Cache the result
                    _embedding_cache[text_hash] = embedding
                    return embedding

                raise Exception(f"Ollama embedding error - no 'embedding' key in response: {data}")
                
            except requests.exceptions.Timeout:
                last_error = "Ollama embedding request timed out"
                if attempt < retries - 1:
                    time.sleep(1 * (attempt + 1))
                    continue
                raise Exception(last_error)
            except requests.exceptions.ConnectionError:
                last_error = "Cannot connect to Ollama. Please make sure Ollama is running on localhost:11434"
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise Exception(last_error)
        
        raise Exception(last_error or "Failed to get embedding after retries")
        
    except Exception as e:
        print(f"Embedding error: {str(e)}")
        raise Exception(f"Error getting embedding: {str(e)}")

def clear_embedding_cache():
    """Clear the embedding cache"""
    global _embedding_cache
    _embedding_cache.clear()
    print("Embedding cache cleared")
