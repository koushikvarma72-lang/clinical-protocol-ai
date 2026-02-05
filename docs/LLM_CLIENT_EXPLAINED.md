# llm_client.py - Line-by-Line Explanation

**What is this file?**  
This file talks to Ollama (the AI language model). Think of it like a phone that calls an AI assistant and asks it questions.

---

## Complete Code with Explanations

```python
import requests
import traceback
```
**Lines 1-2**: Import libraries.
- `requests`: Used to send messages to Ollama
- `traceback`: Used to show detailed error messages

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:latest"   # Changed from gemma3:4b to llama3.1
```
**Lines 4-5**: Set up configuration.
- `OLLAMA_URL`: The address where Ollama is running
- `MODEL`: The name of the AI model to use (llama3.1)

```python
# Global flag to track if model is warmed up
_model_warmed = False
```
**Lines 7-8**: Create a global variable.
- `_model_warmed`: Tracks whether the model has been warmed up
- `False`: Initially, it hasn't been warmed up

---

## Function 1: warm_up_model()

```python
def warm_up_model():
```
**Line 10**: Define a function that prepares the AI model.

```python
    """Pre-warm the Ollama model with a simple query"""
```
**Line 11**: Documentation explaining what this function does.

```python
    global _model_warmed
```
**Line 12**: Use the global variable `_model_warmed`.
- `global`: This means we're using the variable from outside the function

```python
    if _model_warmed:
        return True
```
**Lines 13-14**: If the model is already warmed up, return immediately.
- `if _model_warmed`: If it's True
- `return True`: Exit the function and return True

```python
    try:
```
**Line 16**: Start a "try" block to handle errors.

```python
        print("Warming up Ollama model...")
```
**Line 17**: Print a message so we know the program is working.

```python
        payload = {
            "model": MODEL,
            "prompt": "Hello, respond with just 'Ready'",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 10
            }
        }
```
**Lines 18-26**: Create a message to send to Ollama.
- `"model"`: Which AI model to use
- `"prompt"`: The question to ask ("Hello, respond with just 'Ready'")
- `"stream"`: False means wait for the complete response
- `"temperature"`: 0.1 means very consistent, predictable responses
- `"num_predict"`: Generate only 10 tokens (words)

```python
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
```
**Line 28**: Send the message to Ollama and wait for a response (up to 30 seconds).

```python
        if response.status_code == 200:
```
**Line 29**: Check if the response was successful (200 is the success code).

```python
            _model_warmed = True
            print("Model warmed up successfully")
            return True
```
**Lines 30-32**: If successful, mark the model as warmed up and return True.

```python
        else:
            print(f"Model warm-up failed: {response.status_code}")
            return False
```
**Lines 33-35**: If not successful, print an error and return False.

```python
    except Exception as e:
        print(f"Model warm-up error: {e}")
        return False
```
**Lines 36-38**: If any error happens, print it and return False.

---

## Function 2: ask_llm()

```python
def ask_llm(prompt: str, timeout: int = 45):
```
**Line 40**: Define a function that asks the AI a question.
- `prompt: str`: The question to ask
- `timeout: int = 45`: Wait up to 45 seconds for a response

```python
    """Ask LLM with optimized settings for natural, human-like responses"""
```
**Line 41**: Documentation explaining what this function does.

```python
    try:
```
**Line 42**: Start a "try" block to handle errors.

```python
        # Try to warm up model if not already done
        if not _model_warmed:
            warm_up_model()
```
**Lines 43-45**: If the model isn't warmed up, warm it up first.

```python
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
```
**Lines 47-59**: Create a message to send to Ollama.
- `"model"`: Which AI model to use
- `"prompt"`: The question to ask
- `"stream"`: False means wait for complete response
- `"temperature"`: 0.2 means consistent, factual responses
- `"num_predict"`: Generate up to 600 tokens (words)
- `"top_p"`: 0.8 means focused but natural responses
- `"repeat_penalty"`: 1.2 means don't repeat words
- `"top_k"`: 30 means choose from top 30 most likely words
- `"num_ctx"`: 2048 means remember 2048 tokens of context
- `"stop"`: Stop generating if we see these phrases

```python
        print(f"Asking LLM to read and respond (timeout: {timeout}s)")
```
**Line 61**: Print a message showing the timeout.

```python
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
```
**Line 62**: Send the message to Ollama and wait for a response.

```python
        if response.status_code != 200:
            print(f"Ollama HTTP error: {response.status_code}")
            return "TIMEOUT_ERROR"
```
**Lines 64-66**: If the response wasn't successful, return an error message.

```python
        data = response.json()
```
**Line 68**: Convert the response from JSON format to a Python dictionary.

```python
        if "response" in data:
```
**Line 70**: Check if the response contains a "response" key.

```python
            answer = data["response"].strip()
```
**Line 71**: Get the response and remove extra spaces.

```python
            # Basic quality check
            if len(answer) < 20:
                return "TIMEOUT_ERROR"
```
**Lines 73-74**: If the response is too short (less than 20 characters), return an error.

```python
            # Clean up the response
            lines = answer.split('\n')
```
**Lines 76-77**: Split the response into lines.

```python
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('Human:', 'User:', 'Question:')):
                    cleaned_lines.append(line)
```
**Lines 78-82**: Clean up the response.
- Loop through each line
- Remove extra spaces
- Skip empty lines and lines that start with "Human:", "User:", or "Question:"
- Add the cleaned line to the list

```python
            return '\n'.join(cleaned_lines)
```
**Line 84**: Join the cleaned lines back together and return them.

```python
        return "TIMEOUT_ERROR"
```
**Line 86**: If there's no "response" key, return an error.

```python
    except requests.exceptions.Timeout:
        print("LLM request timed out")
        return "TIMEOUT_ERROR"
```
**Lines 88-90**: If the request times out, print an error and return "TIMEOUT_ERROR".

```python
    except Exception as e:
        print(f"LLM error: {e}")
        return "TIMEOUT_ERROR"
```
**Lines 91-93**: If any other error happens, print it and return "TIMEOUT_ERROR".

---

## Function 3: ask_llm_quick()

```python
def ask_llm_quick(prompt: str):
```
**Line 95**: Define a function that asks the AI a question quickly.

```python
    """Quick LLM call with very short timeout"""
```
**Line 96**: Documentation explaining what this function does.

```python
    return ask_llm(prompt, timeout=10)  # Reduced from 15 to 10 seconds
```
**Line 97**: Call `ask_llm()` with a 10-second timeout.

---

## What This File Does (Summary)

1. **Warms up the model** - Prepares the AI for use
2. **Asks questions** - Sends prompts to the AI
3. **Gets responses** - Receives and cleans up AI responses
4. **Handles errors** - If something goes wrong, returns error messages
5. **Provides quick option** - `ask_llm_quick()` for fast responses

## How It's Used

Other files call these functions to:
- Ask the AI to answer questions about documents
- Generate summaries
- Extract information
- Create responses

## Simple Analogy

Imagine calling a friend:
- **`warm_up_model()`**: Call your friend to make sure they're awake
- **`ask_llm()`**: Ask your friend a question and wait for an answer
- **`ask_llm_quick()`**: Ask your friend a question but hang up if they take too long

## Configuration Explained

| Setting | Value | Meaning |
|---------|-------|---------|
| temperature | 0.2 | Consistent, factual responses |
| num_predict | 600 | Generate up to 600 words |
| top_p | 0.8 | Focused but natural |
| repeat_penalty | 1.2 | Don't repeat words |
| top_k | 30 | Choose from top 30 words |
| num_ctx | 2048 | Remember 2048 tokens |

## Error Handling

The file handles these problems:
- Ollama not running
- Request timeout
- Invalid response
- Response too short
- Network errors

---

**Total Lines**: 97  
**Complexity**: ⭐⭐ Medium  
**Purpose**: Communicate with Ollama AI model to generate responses
