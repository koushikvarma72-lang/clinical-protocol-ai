from vectordb import get_collection
from embeddings import get_embedding
from llm_client import ask_llm_quick, ask_llm
import traceback
import re


def answer_question_with_evidence(question: str, top_k: int = 8):
    """
    Advanced RAG pipeline that acts like a personal assistant with deep document knowledge
    """
    try:
        collection = get_collection()

        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            return {
                "answer": "I don't have any documents loaded yet. Please upload a clinical protocol document first, and I'll become your personal assistant for that document.",
                "sources": [],
                "evidence": []
            }

        print(f"I have access to {count} document chunks. Let me search for information about: {question}")

        # Step 1: Multi-stage retrieval for comprehensive coverage
        print(f"Analyzing your question: {question}")
        
        # Expand query for better matching
        expanded_query = expand_query(question)
        print(f"Expanded search terms: {expanded_query}")
        
        try:
            query_embedding = get_embedding(expanded_query)
            
            # Validate embedding
            if not query_embedding or not isinstance(query_embedding, list) or len(query_embedding) == 0:
                raise Exception("Empty or invalid embedding returned")
                
            print(f"Generated semantic embedding with {len(query_embedding)} dimensions")
            
        except Exception as embed_error:
            print(f"Embedding error: {embed_error}")
            return {
                "answer": f"I'm having trouble understanding your question due to an embedding error: {str(embed_error)}. Please make sure Ollama is running with the nomic-embed-text model, and try asking your question again.",
                "sources": [],
                "evidence": [],
                "question": question
            }

        # Step 2: Comprehensive retrieval with multiple strategies
        print("Searching through the document comprehensively...")
        
        # Primary search with expanded query
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 3, 15),  # Get more results for better coverage
            include=['documents', 'metadatas', 'distances']
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Also try original question if different from expanded
        if expanded_query != question:
            original_embedding = get_embedding(question)
            original_results = collection.query(
                query_embeddings=[original_embedding],
                n_results=min(top_k, 8),
                include=['documents', 'metadatas', 'distances']
            )
            
            # Merge results, avoiding duplicates
            original_docs = original_results.get("documents", [[]])[0]
            original_metas = original_results.get("metadatas", [[]])[0]
            original_distances = original_results.get("distances", [[]])[0]
            
            for doc, meta, dist in zip(original_docs, original_metas, original_distances):
                if doc not in documents:
                    documents.append(doc)
                    metadatas.append(meta)
                    distances.append(dist)

        if not documents:
            return {
                "answer": f"I searched through the entire document but couldn't find any information specifically related to '{question}'. Could you try rephrasing your question or asking about a different aspect of the protocol?",
                "sources": [],
                "evidence": []
            }

        print(f"Found {len(documents)} potentially relevant sections")
        
        # Step 3: Intelligent relevance filtering and ranking
        evidence_items = []
        sources = set()
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            page_num = metadata.get("page_number", "Unknown")
            source = metadata.get("source", f"Page {page_num}")
            
            # Improved relevance scoring
            max_reasonable_distance = 500
            relevance_score = max(0, (max_reasonable_distance - distance) / max_reasonable_distance)
            
            # More permissive threshold for comprehensive coverage
            if relevance_score < 0.05:  # Very low threshold to catch edge cases
                continue
            
            # Clean and prepare the text
            cleaned_text = clean_and_format_text(doc)
            
            evidence_items.append({
                "text": cleaned_text,
                "original_text": doc,  # Keep original for LLM
                "page_number": page_num,
                "source": source,
                "relevance_score": round(relevance_score, 3),
                "citation_id": i + 1,
                "distance": round(distance, 2)
            })
            
            sources.add(f"Page {page_num}")

        if not evidence_items:
            return {
                "answer": f"I searched through the document but the information about '{question}' seems to be either very technical or not present. Could you try asking a more specific question or about a different topic?",
                "sources": [],
                "evidence": []
            }

        # Sort by relevance score (higher is better)
        evidence_items.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"Selected {len(evidence_items)} relevant sections, top relevance: {evidence_items[0]['relevance_score']}")

        # Step 4: Use LLM for intelligent, conversational response
        try:
            print("Generating intelligent response using LLM...")
            return create_intelligent_response(question, evidence_items[:top_k], sources)
            
        except Exception as e:
            print(f"LLM error: {e}, falling back to structured response...")
            return create_enhanced_fallback(question, evidence_items[:top_k], sources)
        
    except Exception as e:
        error_msg = f"I encountered an error while searching the document: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return {
            "answer": f"I'm sorry, I encountered a technical issue while searching for information about '{question}'. Please try asking your question again, or try a simpler version of your question.",
            "sources": [],
            "evidence": [],
            "question": question
        }


def create_intelligent_response(question: str, evidence_items: list, sources: set):
    """Create an intelligent, conversational response using LLM with focused context"""
    
    # Filter and prepare only the most relevant, clean content
    clean_evidence = []
    for item in evidence_items[:4]:  # Use only top 4 most relevant
        if not is_administrative_content(item['original_text']) and item['relevance_score'] > 0.2:
            clean_evidence.append(item)
    
    if not clean_evidence:
        print("No clean evidence found, using enhanced fallback...")
        return create_enhanced_fallback(question, evidence_items, sources)
    
    # Create focused context
    context_parts = []
    for i, item in enumerate(clean_evidence, 1):
        page_info = f"Page {item['page_number']}"
        context_parts.append(f"[{page_info}] {item['original_text'][:400]}...")  # Limit length
    
    context = "\n\n".join(context_parts)
    
    # Simple, direct prompt for better results
    prompt = f"""Based on the clinical protocol document, answer this question: {question}

Relevant information from the protocol:
{context}

Provide a clear, direct answer based on the information above. Be specific and include relevant details like drug names, doses, criteria, or procedures when mentioned. Keep your response focused and informative.

Answer:"""

    try:
        print("Generating focused LLM response...")
        llm_response = ask_llm(prompt, timeout=20)  # Shorter timeout
        
        if llm_response == "TIMEOUT_ERROR" or "Error" in llm_response or len(llm_response) < 30:
            print("LLM failed, using enhanced fallback...")
            return create_enhanced_fallback(question, evidence_items, sources)
        
        # Clean up the response
        cleaned_response = clean_llm_response(llm_response)
        
        # Add source attribution
        page_list = [f"Page {item['page_number']}" for item in clean_evidence]
        if cleaned_response and not cleaned_response.endswith('.'):
            cleaned_response += '.'
        
        cleaned_response += f"\n\n*Source: {', '.join(set(page_list))} of the protocol document.*"
        
        return {
            "answer": cleaned_response,
            "sources": list(sources),
            "evidence": evidence_items,
            "question": question,
            "response_type": "intelligent_llm"
        }
        
    except Exception as e:
        print(f"Error in intelligent response generation: {e}")
        return create_enhanced_fallback(question, evidence_items, sources)


def create_enhanced_fallback(question: str, evidence_items: list, sources: set):
    """Enhanced fallback that's more intelligent than the basic structured response"""
    
    # Analyze question for better context
    question_lower = question.lower()
    
    # Determine response style based on question type
    if any(word in question_lower for word in ["what is", "what are", "describe", "explain"]):
        intro = f"Based on my analysis of the protocol document, here's what I found about {question.lower()}:\n\n"
    elif any(word in question_lower for word in ["how", "when", "where"]):
        intro = f"Regarding {question.lower()}, the protocol specifies:\n\n"
    elif any(word in question_lower for word in ["who", "which patients", "participants"]):
        intro = f"According to the protocol, here are the details about {question.lower()}:\n\n"
    else:
        intro = f"I found relevant information in the protocol about your question:\n\n"
    
    # Extract and organize key information more intelligently
    key_information = []
    page_references = []
    
    for item in evidence_items[:5]:  # Use top 5 items
        text = item['original_text']
        page_num = item['page_number']
        relevance = item['relevance_score']
        
        # Skip very low relevance items
        if relevance < 0.15:
            continue
            
        # Extract meaningful sentences
        sentences = text.split('. ')
        best_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 40 and 
                not is_administrative_content(sentence) and
                contains_meaningful_content(sentence, question_lower)):
                best_sentences.append(sentence)
                if len(best_sentences) >= 2:  # Max 2 sentences per chunk
                    break
        
        if best_sentences:
            formatted_info = '. '.join(best_sentences)
            if not formatted_info.endswith('.'):
                formatted_info += '.'
            key_information.append(formatted_info)
            page_references.append(f"Page {page_num}")
    
    # Build the response
    if key_information:
        response = intro
        
        # Add the information in a natural way
        for i, info in enumerate(key_information):
            if i == 0:
                response += f"{info}\n\n"
            elif i == len(key_information) - 1 and len(key_information) > 1:
                response += f"Additionally, {info}\n\n"
            else:
                response += f"Furthermore, {info}\n\n"
        
        # Add source attribution
        unique_pages = list(set(page_references))
        if len(unique_pages) == 1:
            response += f"*This information is from {unique_pages[0]} of the protocol document.*"
        else:
            response += f"*This information is compiled from {', '.join(unique_pages)} of the protocol document.*"
    else:
        # Fallback when no good information is extracted
        response = f"I found some information related to your question in the protocol document, but it appears to be in technical sections that are difficult to summarize clearly. "
        response += f"The relevant information appears on {', '.join(list(sources))}. "
        response += f"You might want to ask a more specific question or try rephrasing your query."
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": evidence_items,
        "question": question,
        "response_type": "enhanced_fallback"
    }


def create_conversational_response(question: str, top_k: int = 8):
    """
    Create intelligent, conversational responses that act like a personal assistant
    who has deep knowledge of the document - without relying on slow LLM calls
    """
    try:
        collection = get_collection()
        count = collection.count()
        
        if count == 0:
            return {
                "answer": "I don't have any documents loaded yet. Please upload a clinical protocol document first, and I'll become your personal assistant for that document.",
                "sources": [],
                "evidence": []
            }

        print(f"I have access to {count} document chunks. Analyzing your question: {question}")

        # Enhanced query processing
        expanded_query = expand_query(question)
        query_embedding = get_embedding(expanded_query)
        
        # Multi-strategy retrieval for comprehensive coverage
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 2, 16),
            include=['documents', 'metadatas', 'distances']
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return {
                "answer": f"I searched through the entire document but couldn't find specific information about '{question}'. Could you try asking about a different aspect of the protocol, or rephrase your question?",
                "sources": [],
                "evidence": []
            }

        # Intelligent content processing and filtering
        relevant_content = []
        sources = set()
        
        for doc, metadata, distance in zip(documents, metadatas, distances):
            page_num = metadata.get("page_number", "Unknown")
            
            # Calculate relevance
            max_reasonable_distance = 500
            relevance_score = max(0, (max_reasonable_distance - distance) / max_reasonable_distance)
            
            if relevance_score < 0.1:
                continue
                
            # Skip administrative content
            if is_administrative_content(doc):
                continue
                
            relevant_content.append({
                "text": doc,
                "page_number": page_num,
                "relevance_score": relevance_score
            })
            sources.add(f"Page {page_num}")

        if not relevant_content:
            return {
                "answer": f"I found some references to '{question}' in the document, but they appear to be in technical or administrative sections. Could you try asking a more specific question about the clinical aspects of the protocol?",
                "sources": list(sources) if sources else [],
                "evidence": []
            }

        # Sort by relevance
        relevant_content.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Create intelligent, conversational response
        return create_smart_conversational_answer(question, relevant_content[:top_k], sources)
        
    except Exception as e:
        return {
            "answer": f"I encountered an issue while analyzing your question about '{question}'. Please try asking again or rephrase your question.",
            "sources": [],
            "evidence": []
        }


def create_smart_conversational_answer(question: str, content_items: list, sources: set):
    """
    Create intelligent, conversational answers that sound like a knowledgeable assistant
    """
    question_lower = question.lower()
    
    # Analyze question intent and content to provide contextual responses
    if 'drug' in question_lower or 'medication' in question_lower or 'compound' in question_lower:
        return create_drug_focused_response(question, content_items, sources)
    elif any(word in question_lower for word in ['objective', 'purpose', 'goal', 'aim']):
        return create_objective_focused_response(question, content_items, sources)
    elif any(word in question_lower for word in ['inclusion', 'exclusion', 'criteria', 'eligible']):
        return create_criteria_focused_response(question, content_items, sources)
    elif any(word in question_lower for word in ['safety', 'adverse', 'side effect', 'risk']):
        return create_safety_focused_response(question, content_items, sources)
    elif any(word in question_lower for word in ['design', 'methodology', 'how', 'conducted']):
        return create_design_focused_response(question, content_items, sources)
    elif any(word in question_lower for word in ['dose', 'dosage', 'amount', 'mg']):
        return create_dose_focused_response(question, content_items, sources)
    else:
        return create_general_conversational_response(question, content_items, sources)


def create_drug_focused_response(question: str, content_items: list, sources: set):
    """Create response focused on drug/medication information"""
    
    # Look for drug name and details
    drug_info = []
    for item in content_items:
        text = item['text'].lower()
        if 'tak-653' in text:
            # Extract relevant drug information
            sentences = item['text'].split('.')
            for sentence in sentences:
                if 'tak-653' in sentence.lower() and len(sentence.strip()) > 20:
                    drug_info.append(sentence.strip())
                    break
    
    if drug_info:
        response = "The drug being tested in this study is **TAK-653**. "
        
        # Add specific details found
        for info in drug_info[:2]:  # Use top 2 pieces of info
            if 'tablet' in info.lower():
                response += f"It's formulated as {info.lower()}. "
            elif 'dose' in info.lower() or 'mg' in info.lower():
                response += f"Regarding dosing: {info}. "
            elif 'manufactured' in info.lower():
                response += f"{info}. "
        
        response += f"\n\n*This information is from {', '.join(sources)} of the protocol document.*"
    else:
        response = "Based on my analysis of the protocol, the study drug is **TAK-653**. I can see references to this compound throughout the document, though the specific details about its properties and formulation are mentioned in the technical sections. "
        response += f"You can find more details on {', '.join(sources)}."
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }


def create_objective_focused_response(question: str, content_items: list, sources: set):
    """Create response focused on study objectives"""
    
    objective_info = []
    for item in content_items:
        text = item['text']
        if any(word in text.lower() for word in ['objective', 'purpose', 'primary endpoint', 'aim']):
            # Extract objective-related sentences
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['objective', 'purpose', 'primary', 'endpoint']) and len(sentence.strip()) > 30:
                    objective_info.append(sentence.strip())
    
    if objective_info:
        response = "Based on my analysis of the protocol, here's what this study aims to achieve:\n\n"
        
        # Organize the information
        primary_info = [info for info in objective_info if 'primary' in info.lower()]
        other_info = [info for info in objective_info if 'primary' not in info.lower()]
        
        if primary_info:
            response += f"**Primary Objective:** {primary_info[0]}\n\n"
        
        if other_info:
            response += f"**Additional Details:** {other_info[0]}"
        
        response += f"\n\n*This information is compiled from {', '.join(sources)} of the protocol document.*"
    else:
        response = "I can see that this protocol has specific objectives and endpoints defined, but the detailed information appears to be in technical sections of the document. "
        response += f"The relevant information is located on {', '.join(sources)}. Could you ask a more specific question about what aspect of the study objectives you'd like to know?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }


def create_general_conversational_response(question: str, content_items: list, sources: set):
    """Create a general conversational response for any question"""
    
    # Extract the most relevant information
    key_points = []
    for item in content_items[:3]:  # Use top 3 most relevant
        text = item['text']
        
        # Extract meaningful sentences
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 40 and 
                not is_administrative_content(sentence) and
                any(word in sentence.lower() for word in question.lower().split())):
                key_points.append(sentence)
                break
    
    if key_points:
        response = f"Regarding your question about {question.lower()}, here's what I found in the protocol:\n\n"
        
        for i, point in enumerate(key_points, 1):
            response += f"{i}. {point}.\n\n"
        
        response += f"*This information is from {', '.join(sources)} of the protocol document.*"
    else:
        response = f"I found some information related to '{question}' in the protocol document. "
        response += f"The relevant sections are on {', '.join(sources)}. "
        response += "Could you ask a more specific question or try rephrasing to help me provide a better answer?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }


def create_criteria_focused_response(question: str, content_items: list, sources: set):
    """Create response focused on inclusion/exclusion criteria"""
    
    criteria_info = []
    question_type = "inclusion" if "inclusion" in question.lower() else "exclusion" if "exclusion" in question.lower() else "criteria"
    
    for item in content_items:
        text = item['text']
        if any(word in text.lower() for word in ['criteria', 'eligible', 'inclusion', 'exclusion']):
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['criteria', 'eligible', 'must', 'cannot', 'exclude']) and len(sentence.strip()) > 20:
                    criteria_info.append(sentence.strip())
    
    if criteria_info:
        if question_type == "inclusion":
            response = "**Who can participate in this study:**\n\n"
        elif question_type == "exclusion":
            response = "**Who cannot participate in this study:**\n\n"
        else:
            response = "**Participant criteria for this study:**\n\n"
        
        for i, criteria in enumerate(criteria_info[:4], 1):
            response += f"• {criteria}\n\n"
        
        response += f"*This information is from {', '.join(sources)} of the protocol document.*"
    else:
        response = f"I can see that this protocol has specific {question_type} criteria defined. "
        response += f"The detailed criteria are outlined on {', '.join(sources)}. "
        response += "Would you like me to look for more specific aspects of the eligibility requirements?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }


def create_safety_focused_response(question: str, content_items: list, sources: set):
    """Create response focused on safety information"""
    
    safety_info = []
    for item in content_items:
        text = item['text']
        if any(word in text.lower() for word in ['safety', 'adverse', 'monitoring', 'risk', 'side effect']):
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['safety', 'adverse', 'monitor', 'risk']) and len(sentence.strip()) > 30:
                    safety_info.append(sentence.strip())
    
    if safety_info:
        response = "**Safety measures and monitoring in this study:**\n\n"
        
        for i, info in enumerate(safety_info[:3], 1):
            response += f"• {info}\n\n"
        
        response += f"*This information is from {', '.join(sources)} of the protocol document.*"
    else:
        response = "This protocol includes comprehensive safety monitoring procedures. "
        response += f"The detailed safety information is outlined on {', '.join(sources)}. "
        response += "Would you like me to look for specific aspects of safety monitoring or adverse event reporting?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }


def create_design_focused_response(question: str, content_items: list, sources: set):
    """Create response focused on study design"""
    
    design_info = []
    for item in content_items:
        text = item['text']
        if any(word in text.lower() for word in ['design', 'randomized', 'controlled', 'phase', 'methodology']):
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['design', 'randomized', 'phase', 'controlled']) and len(sentence.strip()) > 25:
                    design_info.append(sentence.strip())
    
    if design_info:
        response = "**How this study is designed and conducted:**\n\n"
        
        for i, info in enumerate(design_info[:3], 1):
            response += f"• {info}\n\n"
        
        response += f"*This information is from {', '.join(sources)} of the protocol document.*"
    else:
        response = "This protocol outlines a specific study design and methodology. "
        response += f"The design details are described on {', '.join(sources)}. "
        response += "Would you like me to look for specific aspects of the study design or methodology?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }


def create_dose_focused_response(question: str, content_items: list, sources: set):
    """Create response focused on dosing information"""
    
    dose_info = []
    for item in content_items:
        text = item['text']
        if any(word in text.lower() for word in ['dose', 'mg', 'dosage', 'administration']):
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['dose', 'mg', 'dosage']) and len(sentence.strip()) > 20:
                    dose_info.append(sentence.strip())
    
    if dose_info:
        response = "**Dosing information for this study:**\n\n"
        
        for i, info in enumerate(dose_info[:3], 1):
            response += f"• {info}\n\n"
        
        response += f"*This information is from {', '.join(sources)} of the protocol document.*"
    else:
        response = "This protocol includes specific dosing regimens and administration details. "
        response += f"The dosing information is outlined on {', '.join(sources)}. "
        response += "Would you like me to look for specific dose levels or administration procedures?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": item["text"], "page_number": item["page_number"], "relevance_score": item["relevance_score"]} for item in content_items],
        "question": question,
        "response_type": "conversational_assistant"
    }
    """Create a structured, human-readable fallback response when LLM fails"""
    
    # Analyze the question to provide better context
    question_lower = question.lower()
    
    if "objective" in question_lower or "purpose" in question_lower:
        intro = "**What This Study Is About:**\n"
        summary = "This clinical trial aims to:"
    elif "inclusion" in question_lower:
        intro = "**Who Can Join This Study:**\n"
        summary = "You may be eligible if you:"
    elif "exclusion" in question_lower:
        intro = "**Who Cannot Join This Study:**\n"
        summary = "You cannot participate if you:"
    elif "design" in question_lower:
        intro = "**How This Study Works:**\n"
        summary = "The study is designed as:"
    elif "endpoint" in question_lower:
        intro = "**What We're Measuring:**\n"
        summary = "This study will track:"
    elif "safety" in question_lower:
        intro = "**Safety Measures:**\n"
        summary = "To keep participants safe, this study includes:"
    else:
        intro = f"**About {question}:**\n"
        summary = "Based on the protocol:"
    
    fallback_answer = intro + "\n"
    
    # Extract key points from the evidence with better filtering
    key_points = []
    for item in evidence_items[:5]:  # Check more items to find good content
        text = clean_and_format_text(item['text'])
        
        # Skip if text contains mostly technical/administrative content
        if is_administrative_content(text):
            continue
            
        # Try to extract meaningful sentences
        sentences = text.split('. ')
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 30 and 
                not is_administrative_content(sentence) and
                contains_meaningful_content(sentence, question_lower)):
                key_points.append(f"• {sentence}")
                break  # Only take one good sentence per chunk
        
        # Stop if we have enough good points
        if len(key_points) >= 4:
            break
    
    if key_points:
        fallback_answer += f"{summary}\n\n"
        fallback_answer += "\n".join(key_points[:4])  # Max 4 bullet points
        fallback_answer += f"\n\n*Information found on: {', '.join(sources)}*"
    else:
        # If we can't find meaningful content, provide a helpful message
        fallback_answer += f"I found some information about your question, but it appears to be in technical sections of the protocol. "
        fallback_answer += f"The relevant information might be on {', '.join(sources)}, but it's presented in very technical language.\n\n"
        fallback_answer += "**Suggestion:** Try asking a more specific question like:\n"
        
        if "objective" in question_lower or "purpose" in question_lower:
            fallback_answer += "• 'What is this study trying to find out?'\n• 'What drug is being tested?'"
        elif "safety" in question_lower:
            fallback_answer += "• 'How are participants monitored for safety?'\n• 'What side effects are they watching for?'"
        else:
            fallback_answer += "• Try rephrasing your question\n• Ask about specific aspects like safety, eligibility, or study design"
    
    return {
        "answer": fallback_answer,
        "sources": list(sources),
        "evidence": evidence_items,
        "question": question
    }

def expand_query(question: str) -> str:
    """Expand query with related terms for comprehensive document search"""
    question_lower = question.lower()
    
    # More comprehensive expansion terms for clinical protocols
    expansions = {
        'primary endpoint': ['primary endpoint', 'primary outcome', 'main outcome', 'primary objective', 'efficacy endpoint', 'primary efficacy', 'main goal'],
        'secondary endpoint': ['secondary endpoint', 'secondary outcome', 'secondary objective', 'exploratory endpoint'],
        'endpoint': ['endpoint', 'outcome', 'objective', 'measure', 'assessment', 'evaluation', 'result'],
        'safety': ['safety', 'adverse event', 'side effect', 'tolerability', 'toxicity', 'monitoring', 'AE', 'SAE', 'serious adverse event'],
        'inclusion': ['inclusion criteria', 'eligibility criteria', 'participant criteria', 'enrollment criteria', 'eligible', 'qualify'],
        'exclusion': ['exclusion criteria', 'ineligibility', 'contraindication', 'excluded', 'not eligible'],
        'objective': ['objective', 'purpose', 'aim', 'goal', 'rationale', 'hypothesis'],
        'design': ['study design', 'trial design', 'methodology', 'protocol design', 'randomized', 'controlled', 'blinded'],
        'dose': ['dose', 'dosage', 'administration', 'treatment regimen', 'dosing', 'mg', 'milligram'],
        'population': ['population', 'patients', 'subjects', 'participants', 'enrollment', 'sample size'],
        'duration': ['duration', 'length', 'period', 'time', 'weeks', 'months', 'days'],
        'efficacy': ['efficacy', 'effectiveness', 'response', 'benefit', 'improvement'],
        'biomarker': ['biomarker', 'marker', 'laboratory', 'lab', 'test', 'measurement'],
        'randomization': ['randomization', 'randomized', 'allocation', 'assignment', 'stratification'],
        'blinding': ['blinding', 'blind', 'masked', 'double-blind', 'single-blind'],
        'statistics': ['statistics', 'statistical', 'analysis', 'power', 'sample size', 'significance'],
        'monitoring': ['monitoring', 'oversight', 'safety monitoring', 'DSMB', 'data monitoring'],
        'withdrawal': ['withdrawal', 'discontinuation', 'dropout', 'early termination'],
        'protocol': ['protocol', 'study protocol', 'clinical protocol', 'trial protocol']
    }
    
    # Find the best matching expansion
    best_match = None
    max_matches = 0
    
    for key, terms in expansions.items():
        matches = sum(1 for term in key.split() if term in question_lower)
        if matches > max_matches:
            max_matches = matches
            best_match = key
    
    # If we found a good match, expand the query
    if best_match and max_matches > 0:
        expansion_terms = expansions[best_match]
        # Add the most relevant expansion terms
        expanded = f"{question} {' '.join(expansion_terms[:4])}"  # Use top 4 expansion terms
        return expanded
    
    # For questions about specific topics, add general clinical terms
    clinical_terms = ['clinical', 'study', 'trial', 'protocol', 'patient', 'treatment']
    if not any(term in question_lower for term in clinical_terms):
        return f"{question} clinical study protocol"
    
    return question


def try_simple_llm_approach(question: str, evidence_items: list, sources: set):
    """Try a simpler LLM approach when the main one fails"""
    try:
        # Use only the most relevant chunk
        best_item = evidence_items[0] if evidence_items else None
        if not best_item:
            return create_evidence_fallback(question, evidence_items, sources)
        
        clean_text = clean_and_format_text(best_item['text'])
        
        # Very simple prompt for fastest response
        simple_prompt = f"""Q: {question}
Info: {clean_text[:200]}...
A:"""

        llm_answer = ask_llm(simple_prompt, timeout=8)  # Very short timeout
        
        if llm_answer == "TIMEOUT_ERROR" or "Error" in llm_answer:
            return create_evidence_fallback(question, evidence_items, sources)
        
        return {
            "answer": llm_answer,
            "sources": list(sources),
            "evidence": evidence_items,
            "question": question
        }
        
    except Exception:
        return create_evidence_fallback(question, evidence_items, sources)


def is_administrative_content(text: str) -> bool:
    """Check if text contains mostly administrative/technical content that's not useful to users"""
    admin_keywords = [
        'confidential', 'page', 'protocol incorporating amendment', 'study no.',
        'statistical analysis plan', 'data listings', 'methods of analysis',
        'presentation', 'cohorts', 'srd', 'mrd', 'pooled', 'derived data', 
        'raw data', 'study completion data', 'premature termination', 
        'baseline is defined', 'non-missing measurement', 'ecrf', 'crf',
        'source document', 'drug accountability log', 'inventory',
        'regulatory filing', 'correspondence', 'inspection', 'audit',
        'archiving', 'pharmacovigilance', 'takeda pharmaceutical'
    ]
    
    text_lower = text.lower()
    admin_count = sum(1 for keyword in admin_keywords if keyword in text_lower)
    
    # More aggressive filtering
    if admin_count >= 1 or len(text.strip()) < 50:
        return True
    
    # Check for document formatting artifacts
    if any(pattern in text_lower for pattern in [
        'page', 'of 126', 'march 2017', 'amendment no.', 'confidential'
    ]):
        return True
    
    return False


def contains_meaningful_content(sentence: str, question_type: str) -> bool:
    """Check if sentence contains meaningful content relevant to the question"""
    sentence_lower = sentence.lower()
    
    # Skip administrative content first
    if is_administrative_content(sentence):
        return False
    
    # Define meaningful keywords for different question types
    meaningful_keywords = {
        'objective': ['objective', 'purpose', 'aim', 'goal', 'evaluate', 'assess', 'determine', 'investigate', 'primary endpoint'],
        'purpose': ['objective', 'purpose', 'aim', 'goal', 'evaluate', 'assess', 'determine', 'investigate'],
        'drug': ['tak-653', 'compound', 'medication', 'treatment', 'dose', 'mg', 'tablet', 'placebo'],
        'safety': ['safety', 'adverse', 'side effect', 'monitoring', 'risk', 'tolerability', 'dose', 'toxicity'],
        'inclusion': ['inclusion', 'eligible', 'participate', 'criteria', 'must', 'required'],
        'exclusion': ['exclusion', 'exclude', 'cannot', 'not eligible', 'prohibited'],
        'design': ['design', 'randomized', 'controlled', 'phase', 'trial', 'study design', 'methodology'],
        'endpoint': ['endpoint', 'outcome', 'measure', 'primary', 'secondary', 'efficacy']
    }
    
    # Check if sentence contains relevant keywords for the question type
    for q_type, keywords in meaningful_keywords.items():
        if q_type in question_type:
            if any(keyword in sentence_lower for keyword in keywords):
                return True
    
    # General meaningful content indicators
    meaningful_indicators = [
        'patients', 'subjects', 'treatment', 'drug', 'medication', 'therapy',
        'clinical', 'medical', 'health', 'disease', 'condition', 'symptoms',
        'tak-653', 'dose', 'efficacy', 'safety'
    ]
    
    return any(indicator in sentence_lower for indicator in meaningful_indicators)


def clean_and_format_text(text: str) -> str:
    """Clean and format text to make it more readable and user-friendly"""
    import re
    
    # Remove excessive whitespace and line breaks
    text = re.sub(r'\s+', ' ', text)
    
    # Remove technical document artifacts
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'TAK-\d+-\d+', '', text)
    text = re.sub(r'CONFIDENTIAL', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Statistical Analysis Plan', '', text)
    text = re.sub(r'Final \d+ \w+ \d+', '', text)  # Remove dates like "Final 22 August 2017"
    
    # Fix common formatting issues
    text = re.sub(r'\.{3,}', '...', text)  # Replace multiple dots
    text = re.sub(r'\s+([.,;:])', r'\1', text)  # Fix spacing before punctuation
    
    # Remove technical abbreviations that don't help users
    text = re.sub(r'\b(TEAE|AE|PK|PD|SRD|MRD|CCI)\b', lambda m: {
        'TEAE': 'treatment-related side effects',
        'AE': 'adverse events',
        'PK': 'drug levels',
        'PD': 'drug effects',
        'SRD': 'single dose',
        'MRD': 'multiple dose',
        'CCI': 'confidential information'
    }.get(m.group(), m.group()), text)
    
    # Capitalize first letter of sentences
    sentences = text.split('. ')
    formatted_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 3:  # Only process substantial sentences
            sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            formatted_sentences.append(sentence)
    
    text = '. '.join(formatted_sentences)
    
    # Limit length and add ellipsis if needed
    if len(text) > 300:  # Shorter limit for better readability
        text = text[:300].rsplit(' ', 1)[0] + "..."
    
    return text.strip()


def simple_search(question: str, top_k: int = 3):
    """
    Simple search without LLM - return well-formatted, readable chunks
    """
    try:
        collection = get_collection()
        count = collection.count()
        
        if count == 0:
            return "No documents have been uploaded yet. Please upload a protocol document first."

        # Get embedding for the question
        query_embedding = get_embedding(question)
        
        # Search for relevant chunks with metadata
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if not documents:
            return "No relevant information found in the protocol for your question."
        
        # Analyze question to provide better context
        question_lower = question.lower()
        
        if "objective" in question_lower or "purpose" in question_lower:
            response = "**What This Study Is About:**\n\n"
        elif "inclusion" in question_lower:
            response = "**Who Can Join This Study:**\n\n"
        elif "exclusion" in question_lower:
            response = "**Who Cannot Join This Study:**\n\n"
        elif "design" in question_lower:
            response = "**How This Study Works:**\n\n"
        elif "endpoint" in question_lower:
            response = "**What We're Measuring:**\n\n"
        elif "safety" in question_lower:
            response = "**Safety Measures:**\n\n"
        else:
            response = f"**About {question}:**\n\n"
        
        # Extract key points as bullet points with better filtering
        key_points = []
        sources = []
        
        for doc, metadata in zip(documents, metadatas):
            page_num = metadata.get("page_number", "Unknown")
            sources.append(f"Page {page_num}")
            
            # Clean and format the text
            formatted_text = clean_and_format_text(doc)
            
            # Skip administrative content
            if is_administrative_content(formatted_text):
                continue
            
            # Try to extract meaningful sentences
            sentences = formatted_text.split('. ')
            for sentence in sentences[:3]:  # Check first 3 sentences
                sentence = sentence.strip()
                if (len(sentence) > 30 and 
                    not is_administrative_content(sentence) and
                    contains_meaningful_content(sentence, question_lower)):
                    key_points.append(f"• {sentence}")
                    break  # Only one good sentence per chunk
        
        # Add the key points
        if key_points:
            response += "\n".join(key_points[:5])  # Max 5 bullet points
            response += f"\n\n*Information from: {', '.join(set(sources))}*"
        else:
            # Fallback to original format if bullet extraction fails
            for i, (doc, metadata) in enumerate(zip(documents, metadatas), 1):
                page_num = metadata.get("page_number", "Unknown")
                formatted_text = clean_and_format_text(doc)
                response += f"**From Page {page_num}:** {formatted_text}\n\n"
        
        return response
        
    except Exception as e:
        return f"Error searching document: {str(e)}"


def answer_question(question: str, top_k: int = 6):
    """
    Main RAG function - LLM reads relevant PDF chunks and answers like a human
    """
    try:
        collection = get_collection()
        count = collection.count()
        
        if count == 0:
            return {
                "answer": "I don't have any documents to read yet. Please upload a clinical protocol document first.",
                "sources": [],
                "evidence": []
            }

        print(f"I have {count} chunks of the PDF loaded. Let me search for relevant sections about: {question}")

        # Step 1: Find relevant chunks using vector search
        expanded_query = expand_query(question)
        query_embedding = get_embedding(expanded_query)
        
        # Get relevant chunks
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Get more to filter from
            include=['documents', 'metadatas', 'distances']
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return {
                "answer": f"I couldn't find any relevant information about '{question}' in the PDF. Could you try asking about a different topic?",
                "sources": [],
                "evidence": []
            }

        # Step 2: Filter and prepare the most relevant chunks
        relevant_chunks = []
        sources = set()
        
        for doc, metadata, distance in zip(documents, metadatas, distances):
            page_num = metadata.get("page_number", "Unknown")
            
            # Calculate relevance score
            max_reasonable_distance = 500
            relevance_score = max(0, (max_reasonable_distance - distance) / max_reasonable_distance)
            
            # Only include reasonably relevant chunks
            if relevance_score > 0.15:
                relevant_chunks.append({
                    "text": doc,
                    "page_number": page_num,
                    "relevance_score": relevance_score
                })
                sources.add(f"Page {page_num}")

        if not relevant_chunks:
            return {
                "answer": f"I found some references to '{question}' but they don't seem very relevant. Could you try rephrasing your question?",
                "sources": [],
                "evidence": []
            }

        # Sort by relevance and take the best ones
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        best_chunks = relevant_chunks[:top_k]
        
        print(f"Found {len(best_chunks)} relevant sections. Now reading them to answer your question...")

        # Step 3: Have the LLM read the chunks and respond naturally
        return create_human_like_response(question, best_chunks, sources)
        
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        return {
            "answer": f"I encountered an issue while reading the document to answer '{question}'. Please try asking again.",
            "sources": [],
            "evidence": []
        }


def create_human_like_response(question: str, chunks: list, sources: set):
    """
    Have the LLM read the PDF chunks and respond like a human who just read them
    """
    
    # Prepare the context from PDF chunks
    context_text = ""
    for i, chunk in enumerate(chunks, 1):
        page_info = f"[Page {chunk['page_number']}]"
        context_text += f"\nSection {i} {page_info}:\n{chunk['text']}\n"
    
    # Create a prompt that makes the LLM act like a person reading the PDF
    prompt = f"""You are reading a clinical protocol PDF document. Someone has asked you a question, and you have the most relevant sections from the document in front of you. Read these sections and answer the question naturally, as if you're a knowledgeable person who just read the relevant parts of the PDF.

Question: {question}

Relevant sections from the PDF:
{context_text}

Instructions:
- Read the sections above carefully
- Answer the question based on what you just read
- Be conversational and natural, like you're explaining to a colleague
- Include specific details, numbers, or facts when you see them
- If you see the information clearly, state it confidently
- If something isn't clear from these sections, say so honestly
- Reference page numbers naturally when relevant (e.g., "On page 15, it says...")

Answer the question based on what you just read:"""

    try:
        # Ask the LLM to read and respond
        llm_response = ask_llm(prompt, timeout=30)
        
        if llm_response == "TIMEOUT_ERROR":
            print("LLM timed out, creating fallback response...")
            return create_simple_fallback_response(question, chunks, sources)
        
        # Clean up the response
        cleaned_response = clean_response(llm_response)
        
        return {
            "answer": cleaned_response,
            "sources": list(sources),
            "evidence": [{"text": chunk["text"], "page_number": chunk["page_number"], "relevance_score": chunk["relevance_score"]} for chunk in chunks],
            "question": question,
            "response_type": "human_like_llm"
        }
        
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return create_simple_fallback_response(question, chunks, sources)


def create_simple_fallback_response(question: str, chunks: list, sources: set):
    """
    Simple fallback when LLM fails - still try to be conversational
    """
    
    # Extract key information from the chunks
    key_info = []
    for chunk in chunks[:3]:  # Use top 3 chunks
        text = chunk['text']
        page = chunk['page_number']
        
        # Look for sentences that might answer the question
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and any(word in sentence.lower() for word in question.lower().split()):
                key_info.append(f"On page {page}: {sentence}")
                break
    
    if key_info:
        response = f"Based on what I found in the PDF about '{question}':\n\n"
        for info in key_info:
            response += f"• {info}\n\n"
        response += f"*Information from {', '.join(sources)}*"
    else:
        response = f"I found some information about '{question}' on {', '.join(sources)}, but it's in technical sections that are hard to summarize clearly. Could you ask a more specific question?"
    
    return {
        "answer": response,
        "sources": list(sources),
        "evidence": [{"text": chunk["text"], "page_number": chunk["page_number"], "relevance_score": chunk["relevance_score"]} for chunk in chunks],
        "question": question,
        "response_type": "simple_fallback"
    }


def clean_response(response: str) -> str:
    """Clean up the LLM response to make it more natural"""
    import re
    
    # Remove any meta-commentary
    response = re.sub(r'Based on (the|these) (sections?|documents?|information),?\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'According to (the|these) (sections?|documents?),?\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'From what I (can see|read|understand),?\s*', '', response, flags=re.IGNORECASE)
    
    # Clean up formatting
    response = re.sub(r'\n{3,}', '\n\n', response)
    response = response.strip()
    
    return response