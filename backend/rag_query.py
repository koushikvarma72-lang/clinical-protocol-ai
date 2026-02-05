"""
Legacy RAG Query Module - Minimal implementation for backward compatibility
The new_rag_system.py is the primary RAG implementation
"""

from vectordb import get_collection
from embeddings import get_embedding
from typing import Dict, Any, Optional

def answer_question(question: str) -> Dict[str, Any]:
    """
    Legacy function - delegates to new_rag_system
    """
    from new_rag_system import answer_question_new
    return answer_question_new(question)

def simple_search(question: str) -> str:
    """
    Simple keyword-based search without LLM - fallback method
    """
    try:
        collection = get_collection()
        
        # Generate embedding for the question
        question_embedding = get_embedding(question)
        
        # Query the vector database
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=3
        )
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return "No relevant information found in the document."
        
        # Combine results
        documents = results['documents'][0]
        combined_text = "\n\n".join(documents)
        
        return combined_text
    except Exception as e:
        return f"Error during search: {str(e)}"
