# vectordb.py - Line-by-Line Explanation

**What is this file?**  
This file manages the vector database (ChromaDB). Think of it like a smart filing cabinet that stores documents in a way that makes them easy to find by meaning, not just by keywords.

---

## Complete Code with Explanations

```python
import chromadb
```
**Line 1**: Import the ChromaDB library. ChromaDB is a tool that stores and searches through document embeddings (numerical representations of text meaning).

```python
from chromadb.config import Settings
```
**Line 2**: Import the Settings class from ChromaDB. This lets us configure how ChromaDB behaves.

---

```python
def get_collection():
```
**Line 4**: Define a function called `get_collection()`. This function will return a collection (a container) where we store our document chunks.

```python
    client = chromadb.PersistentClient(
        path="chroma_db",   # ← this WILL create folder
        settings=Settings(
            anonymized_telemetry=False
        )
    )
```
**Lines 5-10**: Create a ChromaDB client that saves data permanently to a folder called "chroma_db".
- `PersistentClient`: Means the data stays saved even after the program stops
- `path="chroma_db"`: The folder where data is stored
- `anonymized_telemetry=False`: Don't send usage data to ChromaDB

```python
    collection = client.get_or_create_collection(
        name="clinical_protocol",
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity instead of L2
    )
```
**Lines 12-15**: Get or create a collection named "clinical_protocol".
- `get_or_create_collection`: If the collection exists, use it. If not, create it.
- `name="clinical_protocol"`: The name of our collection
- `metadata={"hnsw:space": "cosine"}`: Use cosine similarity for searching (measures how similar two documents are)

```python
    return collection
```
**Line 17**: Return the collection so other files can use it.

---

## What This File Does (Summary)

1. **Imports tools** - Brings in ChromaDB library
2. **Creates a function** - `get_collection()` 
3. **Sets up storage** - Creates a persistent database folder
4. **Configures search** - Uses cosine similarity for finding similar documents
5. **Returns the collection** - So other files can store and search documents

## How It's Used

Other files call `get_collection()` to:
- Store document embeddings
- Search for similar documents
- Retrieve relevant chunks for questions

## Simple Analogy

Imagine a library:
- **ChromaDB** = The library building
- **Collection** = A section of the library (e.g., Medical Books)
- **Embeddings** = The meaning of each book
- **Cosine similarity** = How similar two books are in meaning

---

**Total Lines**: 17  
**Complexity**: ⭐ Easy  
**Purpose**: Manage the vector database for storing and searching documents
