# new_rag_system.py - Line-by-Line Explanation

**What is this file?**  
This file is the brain of the system. It combines document search with AI to answer questions intelligently. Think of it like a smart librarian who reads documents and answers your questions.

---

## Complete Code with Explanations (Part 1)

```python
#!/usr/bin/env python3
```
**Line 1**: Shebang line. Tells the system to run this file with Python 3.

```python
"""
New RAG System - Robust, Human-like Document Assistant
Built to work reliably with proper LLM integration
"""
```
**Lines 2-5**: Documentation explaining what this file does.
- RAG = Retrieval-Augmented Generation
- This system retrieves documents and uses AI to generate answers

```python
from vectordb import get_collection
from embeddings import get_embedding
import requests
import json
import time
import re
from typing import Dict, List, Any, Optional
```
**Lines 7-13**: Import libraries and functions.
- `get_collection`: Access the vector database
- `get_embedding`: Convert text to numbers
- `requests`: Send HTTP requests
- `json`: Work with JSON data
- `time`: Work with time
- `re`: Regular expressions for pattern matching
- `Dict, List, Any, Optional`: Type hints

```python
# LLM Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:latest"
```
**Lines 15-17**: Set up configuration.
- `OLLAMA_URL`: Where the AI model is running
- `MODEL`: Which AI model to use

---

## Class: DocumentAssistant

```python
class DocumentAssistant:
```
**Line 19**: Define a class called DocumentAssistant.

```python
    """
    A robust document assistant that reads PDFs and answers questions like a human
    """
```
**Lines 20-22**: Documentation explaining what this class does.

```python
    def __init__(self):
```
**Line 24**: Define the constructor (initialization function).

```python
        self.collection = get_collection()
        self.model_ready = False
        self._prepare_model()
```
**Lines 25-27**: Set up the assistant.
- `self.collection`: Get the vector database
- `self.model_ready`: Track if the AI model is ready
- `self._prepare_model()`: Prepare the AI model

---

## Method: _prepare_model()

```python
    def _prepare_model(self):
```
**Line 29**: Define a method that prepares the AI model.

```python
        """Prepare and test the LLM model"""
```
**Line 30**: Documentation explaining what this method does.

```python
        try:
```
**Line 31**: Start a "try" block to handle errors.

```python
            print("Preparing LLM model...")
            # Simple test to ensure model is working
            test_response = self._call_llm_simple("Hello", timeout=10)
```
**Lines 32-34**: Test the AI model.
- Print a message
- Call the AI with a simple "Hello" message
- Wait up to 10 seconds

```python
            if test_response and "error" not in test_response.lower():
                self.model_ready = True
                print("LLM model is ready")
            else:
                print("LLM model test failed, will use fallback responses")
                self.model_ready = False
```
**Lines 35-40**: Check if the test was successful.
- If we got a response and it doesn't contain "error"
- Mark the model as ready
- Otherwise, mark it as not ready

```python
        except Exception as e:
            print(f"LLM preparation failed: {e}")
            self.model_ready = False
```
**Lines 41-43**: If any error happens, mark the model as not ready.

---

## Method: _call_llm_simple()

```python
    def _call_llm_simple(self, prompt: str, timeout: int = 20) -> Optional[str]:
```
**Line 45**: Define a method that calls the AI with a simple prompt.
- `prompt: str`: The text to send to the AI
- `timeout: int = 20`: Wait up to 20 seconds
- `-> Optional[str]`: Returns a string or None

```python
        """Simple, reliable LLM call with minimal configuration"""
```
**Line 46**: Documentation explaining what this method does.

```python
        try:
```
**Line 47**: Start a "try" block to handle errors.

```python
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 400,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
```
**Lines 48-57**: Create a message to send to the AI.
- `"model"`: Which AI model to use
- `"prompt"`: The text to send
- `"stream"`: False means wait for complete response
- `"temperature"`: 0.1 means very consistent responses
- `"num_predict"`: Generate up to 400 words
- `"top_p"`: 0.9 means focused responses
- `"repeat_penalty"`: 1.1 means don't repeat words

```python
            response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
```
**Line 59**: Send the message to the AI and wait for a response.

```python
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    return data["response"].strip()
```
**Lines 61-64**: Check if the response was successful.
- If status code is 200 (success)
- Convert response to JSON
- If it contains "response" key
- Return the response (with spaces removed)

```python
            return None
```
**Line 66**: If anything went wrong, return None.

```python
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None
```
**Lines 68-70**: If any error happens, print it and return None.

---

## Method: _call_llm_for_reading()

```python
    def _call_llm_for_reading(self, prompt: str, timeout: int = 25) -> Optional[str]:
```
**Line 72**: Define a method that calls the AI for reading documents.
- Similar to `_call_llm_simple()` but optimized for reading

```python
        """Optimized LLM call for reading and answering questions"""
```
**Line 73**: Documentation explaining what this method does.

```python
        try:
```
**Line 74**: Start a "try" block to handle errors.

```python
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Low temperature for factual responses
                    "num_predict": 500,  # Reasonable length
                    "top_p": 0.85,
                    "repeat_penalty": 1.15,
                    "top_k": 25,
                    "stop": ["Human:", "Question:", "User:", "\n\nQ:", "\n\nQuestion:"]
                }
            }
```
**Lines 75-86**: Create a message optimized for reading documents.
- `"temperature"`: 0.2 means factual, consistent responses
- `"num_predict"`: Generate up to 500 words
- `"top_p"`: 0.85 means focused but natural
- `"repeat_penalty"`: 1.15 means avoid repetition
- `"top_k"`: 25 means choose from top 25 words
- `"stop"`: Stop generating if we see these phrases

```python
            print(f"Having LLM read document sections (timeout: {timeout}s)...")
            response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
```
**Lines 88-89**: Send the message to the AI and wait for a response.

```python
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    answer = data["response"].strip()
                    # Basic quality check
                    if len(answer) > 20 and not answer.startswith("Error"):
                        return self._clean_llm_response(answer)
```
**Lines 91-97**: Check if the response was successful.
- If status code is 200
- Convert response to JSON
- If it contains "response" key
- Check if the answer is long enough and doesn't start with "Error"
- Clean up the response and return it

---

## What This File Does (Summary)

1. **Initializes the assistant** - Sets up the vector database and AI model
2. **Prepares the model** - Tests if the AI is working
3. **Calls the AI** - Sends prompts to the AI and gets responses
4. **Handles errors** - If something goes wrong, uses fallback responses

## How It's Used

Other files call this class to:
- Answer questions about documents
- Read and understand document content
- Generate intelligent responses

## Simple Analogy

Imagine a smart librarian:
- **DocumentAssistant** = The librarian
- **_prepare_model()** = The librarian getting ready for work
- **_call_llm_simple()** = Quick questions to the librarian
- **_call_llm_for_reading()** = Complex questions requiring document reading

## Configuration Explained

| Setting | Value | Meaning |
|---------|-------|---------|
| temperature | 0.2 | Factual, consistent responses |
| num_predict | 500 | Generate up to 500 words |
| top_p | 0.85 | Focused but natural |
| repeat_penalty | 1.15 | Avoid repetition |
| top_k | 25 | Choose from top 25 words |

## Error Handling

The file handles these problems:
- AI model not running
- Request timeout
- Invalid response
- Response too short
- Network errors

---

**Total Lines**: 97+ (continues with more methods)  
**Complexity**: ⭐⭐⭐ Complex  
**Purpose**: Intelligent document reading and question answering using RAG
