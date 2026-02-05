import requests
import traceback

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:latest"   # Changed from gemma3:4b to llama3.1

# Global flag to track if model is warmed up
_model_warmed = False

def warm_up_model():
    """Pre-warm the Ollama model with a simple query"""
    global _model_warmed
    if _model_warmed:
        return True
        
    try:
        print("Warming up Ollama model...")
        payload = {
            "model": MODEL,
            "prompt": "Hello, respond with just 'Ready'",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 10
            }
        }
        
        # Increased timeout to 60 seconds for model warm-up
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            _model_warmed = True
            print("✅ Model warmed up successfully")
            return True
        else:
            print(f"⚠️ Model warm-up failed: {response.status_code}")
            print("   System will use fallback responses")
            return False
    except requests.exceptions.Timeout:
        print("⚠️ Model warm-up timed out (Ollama may still be loading)")
        print("   System will use fallback responses")
        print("   Tip: Make sure Ollama is running with: ollama serve")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print("   Make sure Ollama is running with: ollama serve")
        print("   System will use fallback responses")
        return False
    except Exception as e:
        print(f"⚠️ Model warm-up error: {e}")
        print("   System will use fallback responses")
        return False

def ask_llm(prompt: str, timeout: int = 120):
    """Ask LLM with optimized settings for natural, human-like responses"""
    try:
        # Try to warm up model if not already done
        if not _model_warmed:
            warm_up_model()
            
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,  # Lower for more consistent, factual responses
                "num_predict": 600,  # Reasonable length for natural responses
                "top_p": 0.8,  # Focused but natural
                "repeat_penalty": 1.2,  # Prevent repetition
                "top_k": 30,  # More focused
                "num_ctx": 2048,  # Sufficient context
                "stop": ["Human:", "User:", "Question:", "\n\nQuestion:", "\n\nUser:"]
            }
        }

        print(f"Asking LLM to read and respond (timeout: {timeout}s)")
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        
        if response.status_code != 200:
            print(f"Ollama HTTP error: {response.status_code}")
            return "TIMEOUT_ERROR"
        
        data = response.json()

        if "response" in data:
            answer = data["response"].strip()
            
            # Basic quality check
            if len(answer) < 20:
                return "TIMEOUT_ERROR"
            
            # Clean up the response
            lines = answer.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('Human:', 'User:', 'Question:')):
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)

        return "TIMEOUT_ERROR"
        
    except requests.exceptions.Timeout:
        print("LLM request timed out")
        return "TIMEOUT_ERROR"
    except Exception as e:
        print(f"LLM error: {e}")
        return "TIMEOUT_ERROR"

def ask_llm_quick(prompt: str):
    """Quick LLM call with very short timeout"""
    return ask_llm(prompt, timeout=60)  # 60 seconds for quick calls
