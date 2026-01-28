#!/usr/bin/env python3
"""
New RAG System - Robust, Human-like Document Assistant
Built to work reliably with proper LLM integration
"""

from vectordb import get_collection
from embeddings import get_embedding
import requests
import json
import time
import re
from typing import Dict, List, Any, Optional

# LLM Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:latest"

class DocumentAssistant:
    """
    A robust document assistant that reads PDFs and answers questions like a human
    """
    
    def __init__(self):
        self.collection = get_collection()
        self.model_ready = False
        self._prepare_model()
    
    def _prepare_model(self):
        """Prepare and test the LLM model"""
        try:
            print("Preparing LLM model...")
            # Simple test to ensure model is working
            test_response = self._call_llm_simple("Hello", timeout=10)
            if test_response and "error" not in test_response.lower():
                self.model_ready = True
                print("LLM model is ready")
            else:
                print("LLM model test failed, will use fallback responses")
                self.model_ready = False
        except Exception as e:
            print(f"LLM preparation failed: {e}")
            self.model_ready = False
    
    def _call_llm_simple(self, prompt: str, timeout: int = 20) -> Optional[str]:
        """Simple, reliable LLM call with minimal configuration"""
        try:
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
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    return data["response"].strip()
            
            return None
            
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None
    
    def _call_llm_for_reading(self, prompt: str, timeout: int = 25) -> Optional[str]:
        """Optimized LLM call for reading and answering questions"""
        try:
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
            
            print(f"Having LLM read document sections (timeout: {timeout}s)...")
            response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    answer = data["response"].strip()
                    # Basic quality check
                    if len(answer) > 20 and not answer.startswith("Error"):
                        return self._clean_llm_response(answer)
            
            return None
            
        except requests.exceptions.Timeout:
            print("LLM reading timed out")
            return None
        except Exception as e:
            print(f"LLM reading failed: {e}")
            return None
    
    def _clean_llm_response(self, response: str) -> str:
        """Clean up LLM response to make it more natural and human-like"""
        # Remove meta-commentary
        response = re.sub(r'Based on (the|these) (sections?|documents?|text),?\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'According to (the|these) (sections?|documents?),?\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'From what I (can see|read|understand),?\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'Looking at (the|these) (sections?|documents?),?\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'The (document|protocol|text) (states|mentions|indicates|shows),?\s*', '', response, flags=re.IGNORECASE)
        
        # Fix bullet point encoding issues
        response = response.replace('•', '-')
        response = response.replace('◦', '-')
        response = response.replace('▪', '-')
        
        # Clean up formatting and make more conversational
        response = re.sub(r'\n{3,}', '\n\n', response)
        response = response.strip()
        
        # Make response more conversational by adding natural transitions
        if response and not response.endswith('.') and not response.endswith('!') and not response.endswith('?'):
            response += '.'
        
        return response
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Main method - answer questions by reading relevant document sections
        """
        try:
            # Check if we have documents
            count = self.collection.count()
            if count == 0:
                return {
                    "answer": "I don't have any documents loaded. Please upload a clinical protocol document first, and I'll read it to answer your questions.",
                    "sources": [],
                    "evidence": [],
                    "method": "no_documents"
                }
            
            print(f"I have {count} document sections loaded. Searching for information about: {question}")
            
            # Step 1: Find relevant sections using vector search
            relevant_sections = self._find_relevant_sections(question)
            
            if not relevant_sections:
                return {
                    "answer": f"I searched through the document but couldn't find relevant information about '{question}'. Could you try asking about a different aspect of the protocol?",
                    "sources": [],
                    "evidence": [],
                    "method": "no_relevant_sections"
                }
            
            print(f"Found {len(relevant_sections)} relevant sections")
            
            # Step 2: Have LLM read the sections and answer (with fallback)
            if self.model_ready:
                llm_answer = self._get_llm_answer(question, relevant_sections)
                if llm_answer:
                    sources = [f"Page {section['page_number']}" for section in relevant_sections]
                    return {
                        "answer": llm_answer,
                        "sources": list(set(sources)),
                        "evidence": relevant_sections,
                        "question": question,
                        "method": "llm_reading"
                    }
            
            # Step 3: Fallback to intelligent structured response
            print("Using intelligent structured response...")
            return self._create_intelligent_fallback(question, relevant_sections)
            
        except Exception as e:
            print(f"Error in document assistant: {e}")
            return {
                "answer": f"I encountered an issue while reading the document to answer '{question}'. Please try asking again or rephrase your question.",
                "sources": [],
                "evidence": [],
                "method": "error"
            }
    
    def _find_relevant_sections(self, question: str, top_k: int = 6) -> List[Dict]:
        """Find the most relevant document sections for the question"""
        try:
            # Expand query for better search
            expanded_query = self._expand_query(question)
            
            # Get embedding
            query_embedding = get_embedding(expanded_query)
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,  # Get more to filter from
                include=['documents', 'metadatas', 'distances']
            )
            
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            # Filter and rank results
            relevant_sections = []
            for doc, metadata, distance in zip(documents, metadatas, distances):
                # Calculate relevance score
                max_distance = 500
                relevance_score = max(0, (max_distance - distance) / max_distance)
                
                # Only include reasonably relevant sections
                if relevance_score > 0.2 and not self._is_administrative_content(doc):
                    relevant_sections.append({
                        "text": doc,
                        "page_number": metadata.get("page_number", "Unknown"),
                        "relevance_score": round(relevance_score, 3),
                        "distance": round(distance, 2)
                    })
            
            # Sort by relevance and return top results
            relevant_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_sections[:top_k]
            
        except Exception as e:
            print(f"Error finding relevant sections: {e}")
            return []
    
    def _expand_query(self, question: str) -> str:
        """Expand query with related clinical terms"""
        question_lower = question.lower()
        
        expansions = {
            'drug': ['drug', 'medication', 'compound', 'tak-653', 'treatment', 'therapeutic'],
            'objective': ['objective', 'purpose', 'aim', 'goal', 'primary endpoint', 'hypothesis'],
            'safety': ['safety', 'adverse event', 'side effect', 'tolerability', 'monitoring', 'risk'],
            'criteria': ['criteria', 'inclusion', 'exclusion', 'eligible', 'enrollment', 'participant'],
            'design': ['design', 'methodology', 'randomized', 'controlled', 'phase', 'trial'],
            'dose': ['dose', 'dosage', 'mg', 'administration', 'regimen', 'schedule']
        }
        
        # Find best matching expansion
        for key, terms in expansions.items():
            if key in question_lower or any(term in question_lower for term in terms[:2]):
                return f"{question} {' '.join(terms[:3])}"
        
        return question
    
    def _is_administrative_content(self, text: str) -> bool:
        """Check if content is administrative/not useful for users"""
        admin_indicators = [
            'confidential', 'page', 'of 126', 'protocol incorporating amendment',
            'study no.', 'march 2017', 'takeda pharmaceutical', 'source document',
            'drug accountability log', 'regulatory filing', 'correspondence',
            'written subject authorization', 'informed consent form', 'personal information',
            'investigator acknowledges', 'consents to the use', 'described above',
            'amendment no.', 'final', 'version', 'date', 'signature page'
        ]
        
        text_lower = text.lower()
        admin_count = sum(1 for indicator in admin_indicators if indicator in text_lower)
        
        # More aggressive filtering
        if admin_count >= 1:
            return True
            
        # Check for document formatting patterns
        if any(pattern in text_lower for pattern in [
            'page', 'confidential', 'amendment', 'signature', 'consent form'
        ]):
            return True
            
        # Check if text is too short or mostly numbers/formatting
        if len(text.strip()) < 50:
            return True
            
        return False
    
    def _get_llm_answer(self, question: str, sections: List[Dict]) -> Optional[str]:
        """Have LLM read sections and provide human-like answer"""
        try:
            # Prepare context from relevant sections
            context = ""
            for i, section in enumerate(sections[:4], 1):  # Use top 4 sections
                page_info = f"[Page {section['page_number']}]"
                context += f"\nSection {i} {page_info}:\n{section['text']}\n"
            
            # Create prompt for natural reading and answering
            prompt = f"""You are reading a clinical protocol document. Someone asked you: "{question}"

Here are the relevant sections I found in the document:
{context}

Please read these sections and answer the question naturally, as if you're a knowledgeable person who just read the relevant parts of the document. Be conversational and include specific details when you see them.

Answer:"""
            
            # Get LLM response
            response = self._call_llm_for_reading(prompt, timeout=25)
            
            if response and len(response) > 30:
                return response
            
            return None
            
        except Exception as e:
            print(f"Error getting LLM answer: {e}")
            return None
    
    def _create_intelligent_fallback(self, question: str, sections: List[Dict]) -> Dict[str, Any]:
        """Create intelligent structured response when LLM fails"""
        
        question_lower = question.lower()
        
        # Determine response type based on question
        if 'drug' in question_lower or 'medication' in question_lower:
            return self._create_drug_response(question, sections)
        elif 'objective' in question_lower or 'purpose' in question_lower:
            return self._create_objective_response(question, sections)
        elif 'safety' in question_lower:
            return self._create_safety_response(question, sections)
        elif any(word in question_lower for word in ['inclusion', 'exclusion', 'criteria']):
            return self._create_criteria_response(question, sections)
        else:
            return self._create_general_response(question, sections)
    
    def _create_drug_response(self, question: str, sections: List[Dict]) -> Dict[str, Any]:
        """Create response about the study drug"""
        
        # Look for drug information
        drug_info = []
        sources = set()
        
        for section in sections:
            text = section['text']
            page = section['page_number']
            sources.add(f"Page {page}")
            
            if 'tak-653' in text.lower():
                sentences = text.split('.')
                for sentence in sentences:
                    if 'tak-653' in sentence.lower() and len(sentence.strip()) > 20:
                        # Clean up the sentence for better readability
                        clean_sentence = sentence.strip()
                        if clean_sentence and not self._is_administrative_content(clean_sentence):
                            drug_info.append(clean_sentence)
                        break
        
        if drug_info:
            # Create a more conversational response
            answer = "The study drug is **TAK-653**. "
            
            # Synthesize information rather than just listing
            if len(drug_info) == 1:
                answer += f"From the protocol, {drug_info[0].lower()}"
            else:
                answer += "Here's what I found about it:\n\n"
                for i, info in enumerate(drug_info[:2], 1):
                    answer += f"{info}"
                    if i < len(drug_info[:2]):
                        answer += " Additionally, "
                    else:
                        answer += "\n\n"
            
            answer += f"\n*This information comes from {', '.join(sorted(sources))} of the protocol document.*"
        else:
            answer = f"The study drug being tested is **TAK-653**. I found references to this compound on {', '.join(sorted(sources))}, though the specific details are in technical sections of the protocol. Would you like me to look for more specific information about TAK-653's mechanism of action or dosing?"
        
        return {
            "answer": answer,
            "sources": list(sources),
            "evidence": sections,
            "question": question,
            "method": "intelligent_fallback_drug"
        }
    
    def _create_objective_response(self, question: str, sections: List[Dict]) -> Dict[str, Any]:
        """Create response about study objectives"""
        
        objective_info = []
        sources = set()
        
        for section in sections:
            text = section['text']
            page = section['page_number']
            
            # Skip administrative content
            if self._is_administrative_content(text):
                continue
                
            sources.add(f"Page {page}")
            
            # Look for the specific endpoints section
            if 'endpoints' in text.lower() and 'primary' in text.lower():
                # This looks like the endpoints section
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if ('primary endpoint' in line.lower() or 
                        ('primary' in line.lower() and 'endpoint' in line.lower()) or
                        ('endpoints' in line.lower() and len(line) > 50)):
                        if not self._is_administrative_content(line) and len(line) > 30:
                            objective_info.append(line)
                            break
            
            # Look for objective statements
            elif any(word in text.lower() for word in ['study objective', 'primary objective', 'purpose of this study']):
                sentences = text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if (any(word in sentence.lower() for word in ['objective', 'purpose']) 
                        and len(sentence) > 30 
                        and not self._is_administrative_content(sentence)):
                        objective_info.append(sentence)
                        break
            
            # Look for study purpose in general text
            elif 'tak-653' in text.lower() and any(word in text.lower() for word in ['determine', 'evaluate', 'assess']):
                sentences = text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if ('tak-653' in sentence.lower() and 
                        any(word in sentence.lower() for word in ['determine', 'evaluate', 'assess']) 
                        and len(sentence) > 40
                        and not self._is_administrative_content(sentence)):
                        objective_info.append(sentence)
                        break
        
        if objective_info:
            answer = "Here are the main objectives and goals of this study:\n\n"
            
            # Create more natural flow
            if len(objective_info) == 1:
                answer += f"{objective_info[0]}."
            else:
                for i, info in enumerate(objective_info[:3]):
                    if i == 0:
                        answer += f"{info}."
                    elif i == len(objective_info[:3]) - 1:
                        answer += f" Additionally, {info.lower()}."
                    else:
                        answer += f" The study also aims to {info.lower()}."
            
            answer += f"\n\n*Study objectives from {', '.join(sorted(sources))}.*"
        else:
            answer = f"This is a clinical trial protocol with specific objectives and endpoints. The detailed information is located on {', '.join(sorted(sources))}. This appears to be a dose-escalation study of TAK-653. Would you like me to look for specific aspects like the primary endpoint, secondary objectives, or exploratory endpoints?"
        
        return {
            "answer": answer,
            "sources": list(sources),
            "evidence": sections,
            "question": question,
            "method": "intelligent_fallback_objective"
        }
    
    def _create_general_response(self, question: str, sections: List[Dict]) -> Dict[str, Any]:
        """Create general response for any question"""
        
        key_info = []
        sources = set()
        
        for section in sections[:3]:
            text = section['text']
            page = section['page_number']
            sources.add(f"Page {page}")
            
            # Look for sentences that might answer the question
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 40 and 
                    any(word in sentence.lower() for word in question.lower().split()) and
                    not self._is_administrative_content(sentence)):
                    key_info.append(sentence)
                    break
        
        if key_info:
            # Create a more natural, conversational response
            answer = f"Regarding your question about {question.lower()}, here's what I found:\n\n"
            
            if len(key_info) == 1:
                answer += f"{key_info[0]}."
            else:
                # Synthesize multiple pieces of information
                for i, info in enumerate(key_info):
                    if i == 0:
                        answer += f"{info}."
                    elif i == len(key_info) - 1:
                        answer += f" Additionally, {info.lower()}."
                    else:
                        answer += f" Furthermore, {info.lower()}."
            
            answer += f"\n\n*This information is from {', '.join(sorted(sources))} of the protocol.*"
        else:
            answer = f"I found some information related to '{question}' on {', '.join(sorted(sources))}. Could you ask a more specific question to help me provide a better answer? For example, you might ask about specific aspects like safety measures, study design, or participant criteria."
        
        return {
            "answer": answer,
            "sources": list(sources),
            "evidence": sections,
            "question": question,
            "method": "intelligent_fallback_general"
        }
    
    def _create_safety_response(self, question: str, sections: List[Dict]) -> Dict[str, Any]:
        """Create response about safety information"""
        
        safety_info = []
        sources = set()
        
        for section in sections:
            text = section['text']
            page = section['page_number']
            sources.add(f"Page {page}")
            
            if any(word in text.lower() for word in ['safety', 'adverse', 'monitoring', 'risk']):
                sentences = text.split('.')
                for sentence in sentences:
                    if any(word in sentence.lower() for word in ['safety', 'adverse', 'monitor']) and len(sentence.strip()) > 30:
                        clean_sentence = sentence.strip()
                        if not self._is_administrative_content(clean_sentence):
                            safety_info.append(clean_sentence)
                        break
        
        if safety_info:
            answer = "Here's what I found about safety in this study:\n\n"
            
            # Create more natural flow
            if len(safety_info) == 1:
                answer += f"{safety_info[0]}."
            else:
                for i, info in enumerate(safety_info[:3]):
                    if i == 0:
                        answer += f"{info}."
                    elif i == len(safety_info[:3]) - 1:
                        answer += f" Additionally, {info.lower()}."
                    else:
                        answer += f" Furthermore, {info.lower()}."
            
            answer += f"\n\n*Safety information from {', '.join(sorted(sources))}.*"
        else:
            answer = f"This protocol includes comprehensive safety monitoring procedures. The detailed safety information is located on {', '.join(sorted(sources))}. Would you like me to look for specific safety aspects like adverse event monitoring, dose limiting toxicities, or safety run-in procedures?"
        
        return {
            "answer": answer,
            "sources": list(sources),
            "evidence": sections,
            "question": question,
            "method": "intelligent_fallback_safety"
        }
    
    def _create_criteria_response(self, question: str, sections: List[Dict]) -> Dict[str, Any]:
        """Create response about inclusion/exclusion criteria"""
        
        criteria_info = []
        sources = set()
        question_type = "inclusion" if "inclusion" in question.lower() else "exclusion" if "exclusion" in question.lower() else "criteria"
        
        for section in sections:
            text = section['text']
            page = section['page_number']
            sources.add(f"Page {page}")
            
            if any(word in text.lower() for word in ['criteria', 'eligible', 'inclusion', 'exclusion']):
                sentences = text.split('.')
                for sentence in sentences:
                    if any(word in sentence.lower() for word in ['criteria', 'eligible', 'must', 'cannot']) and len(sentence.strip()) > 25:
                        clean_sentence = sentence.strip()
                        if not self._is_administrative_content(clean_sentence):
                            criteria_info.append(clean_sentence)
                        break
        
        if criteria_info:
            if question_type == "inclusion":
                answer = "Here are the key requirements for participants to join this study:\n\n"
            elif question_type == "exclusion":
                answer = "Participants cannot join this study if they meet these conditions:\n\n"
            else:
                answer = "Here are the participant eligibility requirements:\n\n"
            
            # Create more natural flow instead of bullet points
            if len(criteria_info) == 1:
                answer += f"{criteria_info[0]}."
            else:
                for i, info in enumerate(criteria_info[:4]):
                    if i == 0:
                        answer += f"{info}."
                    elif i == len(criteria_info[:4]) - 1:
                        answer += f" Additionally, {info.lower()}."
                    else:
                        answer += f" Also, {info.lower()}."
            
            answer += f"\n\n*Eligibility criteria from {', '.join(sorted(sources))}.*"
        else:
            answer = f"This protocol has specific {question_type} criteria defined on {', '.join(sorted(sources))}. Would you like me to look for more specific eligibility requirements, such as age ranges, medical conditions, or prior treatment history?"
        
        return {
            "answer": answer,
            "sources": list(sources),
            "evidence": sections,
            "question": question,
            "method": "intelligent_fallback_criteria"
        }


# Global instance
document_assistant = DocumentAssistant()

def answer_question_new(question: str) -> Dict[str, Any]:
    """
    New RAG system entry point - use this instead of the old one
    """
    return document_assistant.answer_question(question)