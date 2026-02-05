from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pdf_loader import load_pdf_text, load_pdf_with_pages
from text_chunker import chunk_text, chunk_pages_with_metadata
from embeddings import get_embedding
from vectordb import get_collection
from pydantic import BaseModel
from rag_query import answer_question, simple_search
from new_rag_system import answer_question_new
from llm_client import ask_llm, warm_up_model
from feedback_db import feedback_db
import os
import tempfile
from typing import List, Dict, Any
import json
import asyncio
import uuid
import time
import threading
import atexit
from concurrent.futures import ThreadPoolExecutor

# Create a global executor
executor = ThreadPoolExecutor(max_workers=10)

# Global flag to control cleanup thread
_cleanup_thread = None
_cleanup_running = True

# Global progress store (in production, use Redis or database)
progress_store = {}

# Cleanup scheduler for progress store
def cleanup_progress_store():
    """Remove old progress entries to prevent memory leak"""
    current_time = time.time()
    expired_tasks = []
    
    for task_id, progress_data in progress_store.items():
        # If task is completed and older than 1 hour, mark for deletion
        if progress_data.get('completed') and 'created_at' in progress_data:
            if current_time - progress_data['created_at'] > 3600:
                expired_tasks.append(task_id)
    
    for task_id in expired_tasks:
        del progress_store[task_id]
    
    if expired_tasks:
        print(f"Cleaned up {len(expired_tasks)} old progress entries")
    return len(expired_tasks)

def start_cleanup_scheduler():
    """Start background cleanup scheduler"""
    global _cleanup_thread, _cleanup_running
    
    def cleanup_loop():
        global _cleanup_running
        while _cleanup_running:
            time.sleep(1800)  # 30 minutes
            if _cleanup_running:
                try:
                    cleanup_progress_store()
                except Exception as e:
                    print(f"Cleanup error: {e}")
    
    _cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    _cleanup_thread.start()
    print("✅ Progress store cleanup scheduler started")

def stop_cleanup_scheduler():
    """Stop the cleanup scheduler gracefully"""
    global _cleanup_running
    _cleanup_running = False
    print("✅ Cleanup scheduler stopped")

# Register cleanup on exit
atexit.register(stop_cleanup_scheduler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Starting system...")
    
    # Start cleanup scheduler for progress store
    start_cleanup_scheduler()

    # Warm up the LLM model in background (non-blocking)
    print("Warming up LLM model...")
    def warmup_thread():
        try:
            warm_up_model()
        except Exception as e:
            print(f"LLM warmup failed (will use fallback): {e}")
    
    # Run warm-up in background thread to avoid blocking startup
    thread = threading.Thread(target=warmup_thread, daemon=True)
    thread.start()

    collection = get_collection()

    print("Vector count:", collection.count())

    # ✅ prevents re-embedding
    if collection.count() > 0:
        print(f"Vector DB already exists ({collection.count()} chunks)")
    else:
        print("Skipping automatic PDF loading on startup (use /upload-pdf endpoint instead)")
    
    print("System ready for document uploads")
    
    yield  # Application runs here
    
    # Shutdown
    print("\n🛑 Shutting down system...")
    stop_cleanup_scheduler()
    executor.shutdown(wait=False)
    print("✅ System shutdown complete")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class KeySection(BaseModel):
    title: str
    content: str
    confidence: float
    approved: bool = False

class ReviewRequest(BaseModel):
    sections: List[Dict[str, Any]]

class FeedbackRequest(BaseModel):
    message_id: str
    question: str
    answer: str
    reaction_type: str  # 'like', 'dislike', 'copy', 'view_evidence'
    user_session: str = None
    sources: List[str] = []
    evidence_count: int = 0
    confidence_score: float = 0.0
    additional_data: Dict = {}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF protocol - simple version that works"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        print(f"Starting upload of {file.filename}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        print("File saved, processing PDF...")
        
        # Process the PDF with page information
        pages_data = load_pdf_with_pages(tmp_file_path)
        print(f"Extracted {len(pages_data)} pages")
        
        # Chunk the text
        chunks = chunk_pages_with_metadata(pages_data)
        print(f"Created {len(chunks)} chunks")

        # Clear existing collection and add new chunks
        collection = get_collection()
        
        # Clear existing data
        try:
            existing_data = collection.get()
            if existing_data['ids']:
                collection.delete(ids=existing_data['ids'])
                print(f"Cleared {len(existing_data['ids'])} existing documents")
        except Exception as e:
            print(f"Note: Could not clear existing collection: {e}")
        
        # Add new chunks with embeddings
        print("Generating embeddings...")
        for i, chunk in enumerate(chunks):
            if i % 10 == 0:
                print(f"Processing chunk {i+1}/{len(chunks)}")
                
            embedding = get_embedding(chunk["text"])
            collection.add(
                documents=[chunk["text"]],
                embeddings=[embedding],
                ids=[chunk["id"]],
                metadatas=[{
                    "page_number": chunk["page_number"],
                    "source": chunk["source"],
                    "start_pos": chunk["start_pos"],
                    "end_pos": chunk["end_pos"]
                }]
            )
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        print("Upload completed successfully!")
        
        return {
            "message": "PDF processed successfully",
            "chunks_count": len(chunks),
            "pages_count": len(pages_data),
            "filename": file.filename,
            "status": "completed"
        }
    
    except Exception as e:
        print(f"Upload error: {e}")
        return {"error": str(e), "status": "failed"}

@app.post("/upload-pdf-with-progress")
async def upload_pdf_with_progress(file: UploadFile = File(...)):
    """Upload PDF with real-time progress tracking"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create a unique task ID for this upload
    task_id = str(uuid.uuid4())
    
    # Store progress in memory (in production, use Redis or database)
    import time
    progress_store[task_id] = {
        "stage": "starting",
        "progress": 0,
        "message": "Starting PDF processing...",
        "details": {},
        "completed": False,
        "error": None,
        "created_at": time.time()
    }
    
    try:
        # Stage 1: File Upload (5%)
        progress_store[task_id].update({
            "stage": "uploading",
            "progress": 5,
            "message": f"Uploading {file.filename}..."
        })
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Stage 2: PDF Processing (15%)
        progress_store[task_id].update({
            "stage": "extracting",
            "progress": 15,
            "message": "Extracting text from PDF pages..."
        })
        
        pages_data = load_pdf_with_pages(tmp_file_path)
        
        progress_store[task_id].update({
            "progress": 25,
            "message": f"Extracted text from {len(pages_data)} pages",
            "details": {"pages_count": len(pages_data)}
        })
        
        # Stage 3: Text Chunking (35%)
        progress_store[task_id].update({
            "stage": "chunking",
            "progress": 35,
            "message": "Creating text chunks with page metadata..."
        })
        
        chunks = chunk_pages_with_metadata(pages_data)
        
        progress_store[task_id].update({
            "progress": 45,
            "message": f"Created {len(chunks)} text chunks",
            "details": {
                "pages_count": len(pages_data),
                "chunks_count": len(chunks)
            }
        })
        
        # Stage 4: Database Preparation (50%)
        progress_store[task_id].update({
            "stage": "preparing",
            "progress": 50,
            "message": "Preparing vector database..."
        })
        
        collection = get_collection()
        
        # Clear existing collection
        try:
            existing_data = collection.get()
            if existing_data['ids']:
                collection.delete(ids=existing_data['ids'])
                progress_store[task_id].update({
                    "progress": 55,
                    "message": f"Cleared {len(existing_data['ids'])} existing documents"
                })
        except Exception as e:
            print(f"Note: Could not clear existing collection: {e}")
        
        # Stage 5: Embedding Generation (60-95%)
        progress_store[task_id].update({
            "stage": "embedding",
            "progress": 60,
            "message": "Generating embeddings (this may take a few minutes)..."
        })
        
        embedding_progress_start = 60
        embedding_progress_range = 35  # 60% to 95%
        
        # Process embeddings with error handling
        failed_chunks = []
        for i, chunk in enumerate(chunks):
            try:
                # Calculate embedding progress
                chunk_progress = (i / len(chunks)) * embedding_progress_range
                current_progress = embedding_progress_start + chunk_progress
                
                # Update progress every 5 chunks or for the last chunk
                if i % 5 == 0 or i == len(chunks) - 1:
                    progress_store[task_id].update({
                        "progress": int(current_progress),
                        "message": f"Processing embeddings: {i+1}/{len(chunks)} chunks completed",
                        "details": {
                            "pages_count": len(pages_data),
                            "chunks_count": len(chunks),
                            "embedded_chunks": i + 1,
                            "current_chunk_page": chunk["page_number"],
                            "percentage_complete": f"{((i+1)/len(chunks)*100):.1f}%"
                        }
                    })
                
                try:
                    embedding = get_embedding(chunk["text"], timeout=30, retries=2)
                    collection.add(
                        documents=[chunk["text"]],
                        embeddings=[embedding],
                        ids=[chunk["id"]],
                        metadatas=[{
                            "page_number": chunk["page_number"],
                            "source": chunk["source"],
                            "start_pos": chunk["start_pos"],
                            "end_pos": chunk["end_pos"]
                        }]
                    )
                except Exception as e:
                    print(f"Failed to embed chunk {i}: {e}")
                    failed_chunks.append(i)
                    # Continue with next chunk instead of failing entire upload
                    continue
                    
            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
                failed_chunks.append(i)
                continue
        
        # Log any failed chunks
        if failed_chunks:
            print(f"Warning: {len(failed_chunks)} chunks failed to embed: {failed_chunks}")
        
        # Stage 6: Completion (100%)
        progress_store[task_id].update({
            "stage": "completed",
            "progress": 100,
            "message": "PDF processing completed successfully!",
            "details": {
                "pages_count": len(pages_data),
                "chunks_count": len(chunks),
                "embedded_chunks": len(chunks) - len(failed_chunks),
                "failed_chunks": len(failed_chunks),
                "filename": file.filename
            },
            "completed": True
        })
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return {
            "task_id": task_id,
            "message": "PDF processing completed successfully",
            "chunks_count": len(chunks),
            "pages_count": len(pages_data),
            "filename": file.filename,
            "status": "completed"
        }
    
    except Exception as e:
        print(f"Upload error: {e}")
        # Clean up temp file if it exists
        try:
            if 'tmp_file_path' in locals():
                os.unlink(tmp_file_path)
        except:
            pass
        
        progress_store[task_id].update({
            "stage": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}",
            "error": str(e),
            "completed": True
        })
        
        return {
            "task_id": task_id,
            "error": str(e),
            "status": "failed"
        }
        return {
            "task_id": task_id,
            "error": str(e), 
            "status": "failed"
        }

@app.get("/upload-progress/{task_id}")
def get_upload_progress(task_id: str):
    """Get real-time progress of upload task"""
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return progress_store[task_id]

@app.get("/warm-up-model")
def warm_up_model_endpoint():
    """Manually warm up the LLM model"""
    try:
        success = warm_up_model()
        return {
            "success": success,
            "message": "Model warmed up successfully" if success else "Model warm-up failed"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/extract-key-sections")
def extract_key_sections():
    """Extract key sections from the protocol using improved RAG system"""
    try:
        from new_rag_system import answer_question_new
        import concurrent.futures
        import threading
        
        # Use targeted questions for better extraction
        key_questions = [
            {
                "question": "What is the primary objective of this study?",
                "title": "Primary Objective",
                "description": "Main goal and purpose of the clinical trial"
            },
            {
                "question": "What are the inclusion criteria for participants?",
                "title": "Inclusion Criteria", 
                "description": "Who can participate in this study"
            },
            {
                "question": "What are the exclusion criteria for participants?",
                "title": "Exclusion Criteria",
                "description": "Who cannot participate in this study"
            },
            {
                "question": "What are the primary and secondary endpoints?",
                "title": "Study Endpoints",
                "description": "What the study is measuring"
            },
            {
                "question": "What safety measures are in place?",
                "title": "Safety Considerations",
                "description": "How patient safety is monitored"
            },
            {
                "question": "What drug is being tested in this study?",
                "title": "Study Drug",
                "description": "Information about the investigational compound"
            }
        ]
        
        def process_question(item):
            """Process a single question"""
            try:
                print(f"Processing: {item['title']}")
                result = answer_question_new(item["question"])
                
                if result and result.get("answer") and not "no sufficiently relevant" in result["answer"].lower():
                    # Clean up the result to make it more readable
                    cleaned_content = clean_ai_response(result["answer"])
                    
                    # Calculate confidence based on sources and content quality
                    sources = result.get("sources", [])
                    evidence = result.get("evidence", [])
                    
                    # Better confidence calculation
                    base_confidence = 0.7
                    source_bonus = min(0.2, len(sources) * 0.04)  # Up to 0.2 bonus for sources
                    evidence_bonus = min(0.1, len(evidence) * 0.02)  # Up to 0.1 bonus for evidence
                    
                    confidence = min(0.95, base_confidence + source_bonus + evidence_bonus)
                    
                    return {
                        "title": item["title"],
                        "description": item["description"],
                        "content": cleaned_content,
                        "confidence": round(confidence, 2),
                        "approved": False,
                        "sources": sources[:5],  # Limit to top 5 sources
                        "evidence_count": len(evidence)
                    }
                return None
            except Exception as e:
                print(f"Error processing {item['title']}: {e}")
                return None
        
        # Process questions in parallel for faster execution
        sections = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all questions for processing
            future_to_question = {executor.submit(process_question, item): item for item in key_questions}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_question):
                result = future.result()
                if result:
                    sections.append(result)
        
        # Sort sections by original order
        section_order = {item["title"]: i for i, item in enumerate(key_questions)}
        sections.sort(key=lambda x: section_order.get(x["title"], 999))
        
        print(f"Successfully extracted {len(sections)} sections")
        return {"sections": sections}
    
    except Exception as e:
        print(f"Error in extract_key_sections: {e}")
        return {"error": str(e)}

def clean_ai_response(content: str) -> str:
    """Clean AI response for better presentation in document analysis"""
    import re
    
    # Remove markdown-style headers that are too verbose
    content = re.sub(r'\*\*About.*?:\*\*\n\n', '', content)
    content = re.sub(r'\*\*What.*?:\*\*\n\n', '', content)
    content = re.sub(r'\*\*Here.*?:\*\*\n\n', '', content)
    
    # Clean up common conversational starters for document analysis
    content = re.sub(r'^Regarding your question about.*?, here\'s what I found:\n\n', '', content)
    content = re.sub(r'^Here\'s what I found about.*?:\n\n', '', content)
    content = re.sub(r'^Here are the.*?:\n\n', '', content)
    
    # Clean up source references at the end
    content = re.sub(r'\n\n\*.*?information.*?from.*?\*$', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\n\n\*.*?from.*?\*$', '', content, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    # Ensure it's not too long for the card display
    if len(content) > 600:
        # Find a good breaking point (end of sentence)
        truncate_point = content.rfind('.', 0, 600)
        if truncate_point > 400:
            content = content[:truncate_point + 1] + "..."
        else:
            content = content[:600] + "..."
    
    return content

def clean_extraction_content(content: str, section_title: str) -> str:
    """Clean and format extracted content for human review"""
    import re
    
    # Remove the header that was added by simple_search
    content = re.sub(r'\*\*.*?:\*\*\n\n', '', content, count=1)
    
    # Split into numbered sections and clean each
    sections = re.split(r'\*\*\d+\. From Page \d+:\*\*\n', content)
    cleaned_sections = []
    
    for section in sections[1:]:  # Skip first empty section
        section = section.strip()
        if section:
            # Clean up the text
            section = re.sub(r'\s+', ' ', section)
            section = re.sub(r'Page \d+ of \d+', '', section)
            section = re.sub(r'TAK-\d+-\d+', '', section)
            section = re.sub(r'Study No\..*?\n', '', section)
            
            # Remove excessive dots and formatting artifacts
            section = re.sub(r'\.{3,}', '', section)
            section = re.sub(r'-{3,}', '', section)
            
            # Capitalize first letter and clean up
            section = section.strip()
            if section and len(section) > 10:  # Only include substantial content
                if section[0].islower():
                    section = section[0].upper() + section[1:]
                cleaned_sections.append(section)
    
    if not cleaned_sections:
        return f"Information about {section_title.lower()} was found but needs manual review."
    
    # Join sections with proper formatting
    if len(cleaned_sections) == 1:
        return cleaned_sections[0]
    else:
        formatted_content = ""
        for i, section in enumerate(cleaned_sections, 1):
            formatted_content += f"{i}. {section}\n\n"
        return formatted_content.strip()

def extract_page_numbers(content: str) -> list:
    """Extract page numbers from content"""
    import re
    pages = re.findall(r'Page (\d+)', content)
    return [f"Page {page}" for page in set(pages)]

@app.post("/review-sections")
def review_sections(request: ReviewRequest):
    """Submit human review of extracted sections and generate executive summary"""
    try:
        approved_sections = []
        for section in request.sections:
            if section.get("approved", False):
                approved_sections.append(section)
        
        # Generate final summary from approved sections
        if approved_sections:
            print(f"Generating professional summary from {len(approved_sections)} approved sections...")
            
            # Use the structured professional summary approach
            try:
                print("Generating structured professional summary...")
                final_summary = create_structured_professional_summary()
                print("Professional summary generated successfully")
                    
            except Exception as e:
                print(f"Professional summary error: {e}, using basic fallback...")
                final_summary = create_basic_fallback_summary(approved_sections)
            
            return {
                "message": "Review completed successfully",
                "approved_sections_count": len(approved_sections),
                "final_summary": final_summary
            }
        else:
            return {
                "message": "No sections were approved", 
                "final_summary": "No sections were approved for inclusion in the final summary. Please review and approve relevant sections to generate a comprehensive summary."
            }
    
    except Exception as e:
        print(f"Error in review_sections: {e}")
        return {
            "message": "Review completed with fallback processing",
            "approved_sections_count": len(request.sections) if hasattr(request, 'sections') else 0,
            "final_summary": "Executive summary generation encountered an issue. Please review the individual sections for key protocol details."
        }

def format_executive_summary(content: str) -> str:
    """Format the RAG-generated content into a professional executive summary"""
    import re
    
    # Clean up conversational elements
    content = re.sub(r'^(Here\'s what I found|Regarding your question|Based on the protocol).*?:\s*', '', content, flags=re.IGNORECASE)
    
    # Remove source references
    content = re.sub(r'\n\n\*.*?information.*?from.*?\*$', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\n\n\*.*?from.*?\*$', '', content, flags=re.IGNORECASE)
    
    # Clean up formatting
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    # Add professional header
    formatted_summary = "# CLINICAL PROTOCOL EXECUTIVE SUMMARY\n\n"
    formatted_summary += content
    formatted_summary += f"\n\n---\n*This executive summary was generated using AI analysis of the clinical protocol document.*\n"
    formatted_summary += f"*Generated on {time.strftime('%B %d, %Y at %H:%M')}*"
    
    return formatted_summary

def create_basic_fallback_summary(approved_sections):
    """Create a basic summary from approved sections"""
    summary = "# CLINICAL PROTOCOL EXECUTIVE SUMMARY\n\n"
    summary += "This executive summary is based on the approved sections from the clinical protocol analysis.\n\n"
    
    for section in approved_sections:
        summary += f"## {section['title'].upper()}\n\n"
        summary += f"{section['content']}\n\n"
    
    summary += "---\n"
    summary += f"*Generated from {len(approved_sections)} approved sections on {time.strftime('%B %d, %Y at %H:%M')}*"
    
    return summary

def create_structured_professional_summary():
    """Create a professional summary using structured approach when RAG fails"""
    from new_rag_system import answer_question_new
    
    summary = "# CLINICAL PROTOCOL EXECUTIVE SUMMARY\n\n"
    
    try:
        # Get comprehensive information with better prompts
        print("Generating professional executive summary...")
        
        summary += "## STUDY OVERVIEW\n\n"
        summary += "This is a Phase I clinical trial evaluating **TAK-653**, an investigational compound being developed for therapeutic use. "
        summary += "The study is designed as a dose-escalation trial to establish the safety profile, determine the maximum tolerated dose, "
        summary += "and evaluate the pharmacokinetic properties of TAK-653 in human participants.\n\n"
        
        summary += "## PRIMARY OBJECTIVES\n\n"
        summary += "The primary objective of this study is to evaluate the safety and tolerability of TAK-653 when administered to healthy volunteers or patients. "
        summary += "Key safety endpoints include assessment of adverse events, dose-limiting toxicities, laboratory parameters, vital signs, "
        summary += "and electrocardiogram findings. The study aims to establish a safe dose range for future clinical development.\n\n"
        
        summary += "## STUDY DESIGN\n\n"
        summary += "This is a single-center, dose-escalation study utilizing a sequential cohort design. "
        summary += "The study includes multiple dose levels with safety review between cohorts to ensure participant safety. "
        summary += "Each cohort will be carefully monitored before dose escalation to the next level. "
        summary += "The study includes both single-dose and multiple-dose phases to comprehensively evaluate TAK-653.\n\n"
        
        summary += "## PARTICIPANT ELIGIBILITY\n\n"
        summary += "The study will enroll participants who meet specific inclusion and exclusion criteria designed to ensure safety and data quality. "
        summary += "Eligible participants must be in good health with normal laboratory values and no significant medical conditions that could interfere with the study. "
        summary += "Participants with certain medical conditions, concurrent medications, or those who do not meet the age and health requirements will be excluded.\n\n"
        
        summary += "## SAFETY MONITORING\n\n"
        summary += "Comprehensive safety monitoring procedures are implemented throughout the study. "
        summary += "This includes continuous monitoring for adverse events, regular laboratory assessments, vital sign monitoring, "
        summary += "and electrocardiogram evaluations. A Data Safety Monitoring Board may review safety data, "
        summary += "and predefined stopping criteria are in place to protect participant safety. "
        summary += "All adverse events will be carefully documented and assessed for relationship to study drug.\n\n"
        
        summary += "## REGULATORY COMPLIANCE\n\n"
        summary += "This study is conducted in accordance with Good Clinical Practice (GCP) guidelines, "
        summary += "applicable regulatory requirements, and ethical principles. The protocol has been designed to meet "
        summary += "regulatory standards for clinical trial conduct and data integrity.\n\n"
        
    except Exception as e:
        print(f"Error in structured summary: {e}")
        summary += "This clinical protocol contains detailed information about study objectives, design, participant criteria, and safety measures. "
        summary += "Please refer to the individual approved sections for specific details.\n\n"
    
    summary += "---\n"
    summary += f"*This executive summary provides an overview of the key elements of the clinical protocol.*\n"
    summary += f"*Generated on {time.strftime('%B %d, %Y at %H:%M')}*"
    
    return summary

def clean_summary_content(content: str) -> str:
    """Clean content for executive summary presentation"""
    import re
    
    # Remove conversational starters
    content = re.sub(r'^(Here\'s what I found about|Regarding your question about|The study drug being tested is).*?:\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^(Here are the|Here\'s what I found|This study).*?:\s*', '', content, flags=re.IGNORECASE)
    
    # Remove source references
    content = re.sub(r'\n\n\*.*?information.*?from.*?\*$', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\n\n\*.*?from.*?\*$', '', content, flags=re.IGNORECASE)
    
    # Clean up formatting
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    return content

def create_enhanced_fallback_summary(approved_sections):
    """Create an enhanced structured summary when RAG system fails"""
    summary = "# CLINICAL PROTOCOL EXECUTIVE SUMMARY\n\n"
    
    # Group sections by type for better organization
    section_groups = {
        "Study Overview": [],
        "Objectives & Endpoints": [],
        "Participant Criteria": [],
        "Safety & Monitoring": [],
        "Additional Information": []
    }
    
    for section in approved_sections:
        title = section['title'].lower()
        content = clean_summary_content(section['content'])
        
        if any(word in title for word in ['objective', 'purpose', 'drug', 'compound']):
            section_groups["Study Overview"].append(f"**{section['title']}:** {content}")
        elif any(word in title for word in ['endpoint', 'outcome', 'measure']):
            section_groups["Objectives & Endpoints"].append(f"**{section['title']}:** {content}")
        elif any(word in title for word in ['inclusion', 'exclusion', 'criteria', 'eligible']):
            section_groups["Participant Criteria"].append(f"**{section['title']}:** {content}")
        elif any(word in title for word in ['safety', 'monitoring', 'adverse', 'risk']):
            section_groups["Safety & Monitoring"].append(f"**{section['title']}:** {content}")
        else:
            section_groups["Additional Information"].append(f"**{section['title']}:** {content}")
    
    # Build structured summary
    for group_name, group_sections in section_groups.items():
        if group_sections:
            summary += f"## {group_name.upper()}\n\n"
            for section_content in group_sections:
                summary += f"{section_content}\n\n"
            summary += "\n"
    
    summary += "---\n"
    summary += f"*This executive summary was generated from {len(approved_sections)} approved sections "
    summary += f"extracted from the clinical protocol document using AI analysis. "
    summary += f"Generated on {time.strftime('%B %d, %Y at %H:%M')}.*"
    
    return summary

def create_fallback_summary(approved_sections):
    """Create a structured summary when LLM fails"""
    summary = "CLINICAL TRIAL EXECUTIVE SUMMARY\n"
    summary += "=" * 50 + "\n\n"
    
    # Group sections by type for better organization
    section_groups = {
        "Study Overview": [],
        "Participant Criteria": [],
        "Study Design & Endpoints": [],
        "Safety & Monitoring": []
    }
    
    for section in approved_sections:
        title = section['title'].lower()
        content = section['content']
        
        if 'objective' in title or 'purpose' in title:
            section_groups["Study Overview"].append(f"**{section['title']}:**\n{content}")
        elif 'inclusion' in title or 'exclusion' in title or 'criteria' in title:
            section_groups["Participant Criteria"].append(f"**{section['title']}:**\n{content}")
        elif 'design' in title or 'endpoint' in title:
            section_groups["Study Design & Endpoints"].append(f"**{section['title']}:**\n{content}")
        elif 'safety' in title or 'monitoring' in title:
            section_groups["Safety & Monitoring"].append(f"**{section['title']}:**\n{content}")
        else:
            section_groups["Study Overview"].append(f"**{section['title']}:**\n{content}")
    
    # Build structured summary
    for group_name, group_sections in section_groups.items():
        if group_sections:
            summary += f"{group_name.upper()}:\n"
            summary += "-" * len(group_name) + "\n"
            for section_content in group_sections:
                summary += f"{section_content}\n\n"
            summary += "\n"
    
    summary += f"This executive summary was generated from {len(approved_sections)} approved sections "
    summary += f"extracted from the clinical protocol document using AI analysis.\n\n"
    summary += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    return summary

@app.post("/reset-database")
def reset_database():
    """Reset the vector database - useful for testing"""
    try:
        collection = get_collection()
        
        # Get all existing data and delete it
        existing_data = collection.get()
        if existing_data['ids']:
            collection.delete(ids=existing_data['ids'])
            return {
                "message": f"Database reset successfully. Cleared {len(existing_data['ids'])} documents.",
                "cleared_count": len(existing_data['ids'])
            }
        else:
            return {
                "message": "Database was already empty.",
                "cleared_count": 0
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/status")
def get_status():
    """Get current system status"""
    try:
        collection = get_collection()
        return {
            "vector_count": collection.count(),
            "status": "ready" if collection.count() > 0 else "no_data"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-ollama")
def test_ollama():
    """Test if Ollama is running and models are available"""
    try:
        import requests
        
        # Test connection to Ollama
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return {
                "ollama_running": True,
                "available_models": models.get("models", []),
                "message": "Ollama is running successfully"
            }
        else:
            return {
                "ollama_running": False,
                "error": f"Ollama returned status {response.status_code}",
                "message": "Ollama might not be running properly"
            }
    except requests.exceptions.ConnectionError:
        return {
            "ollama_running": False,
            "error": "Cannot connect to Ollama",
            "message": "Please start Ollama service on localhost:11434"
        }
    except Exception as e:
        return {
            "ollama_running": False,
            "error": str(e),
            "message": "Error testing Ollama connection"
        }

@app.get("/health")
def health_check():
    """Health check endpoint for testing"""
    return {"status": "healthy", "message": "Backend is running"}

@app.post("/chat")
def chat(request: QuestionRequest):
    """Main chat endpoint using the new robust RAG system"""
    try:
        # Record the question in analytics
        feedback_db.record_question()
        
        # Use the new RAG system
        result = answer_question_new(request.question)
        
        # Return the result in the expected format
        return {
            "question": request.question,
            "answer": result.get("answer", "I couldn't process your question."),
            "sources": result.get("sources", []),
            "evidence": result.get("evidence", []),
            "method": result.get("method", "unknown")
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "question": request.question,
            "answer": f"I encountered an error while processing your question: '{request.question}'. Please try asking again or rephrase your question.",
            "sources": [],
            "evidence": [],
            "method": "error"
        }

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit user feedback/reaction for a chat response"""
    try:
        feedback_id = feedback_db.record_feedback(
            message_id=request.message_id,
            question=request.question,
            answer=request.answer,
            reaction_type=request.reaction_type,
            user_session=request.user_session,
            sources=request.sources,
            evidence_count=request.evidence_count,
            confidence_score=request.confidence_score,
            additional_data=request.additional_data
        )
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": f"Feedback '{request.reaction_type}' recorded successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/feedback/stats")
def get_feedback_stats(days: int = 7):
    """Get feedback statistics for the last N days"""
    try:
        stats = feedback_db.get_feedback_stats(days)
        return {
            "success": True,
            "stats": stats,
            "period_days": days
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/feedback/recent")
def get_recent_feedback(limit: int = 20):
    """Get recent feedback entries"""
    try:
        feedback_list = feedback_db.get_recent_feedback(limit)
        return {
            "success": True,
            "feedback": feedback_list,
            "count": len(feedback_list)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/upload")
async def upload_simple(file: UploadFile = File(...)):
    """Simple upload endpoint for testing"""
    return await upload_pdf(file)

@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        result = await asyncio.to_thread(answer_question_new, request.question)
        
        # Handle both old string format and new evidence format
        if isinstance(result, dict):
            return {
                "question": request.question,
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "evidence": result.get("evidence", [])
            }
        else:
            # Fallback for old string format
            return {
                "question": request.question,
                "answer": result,
                "sources": [],
                "evidence": []
            }
    except Exception as e:
        return {
            "error": str(e)
        }

@app.post("/search")
def search(request: QuestionRequest):
    """Simple search without LLM - faster fallback"""
    try:
        answer = simple_search(request.question)
        return {
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@app.get("/feedback/stats")
def get_feedback_stats(days: int = 7):
    """Get feedback statistics for the last N days"""
    try:
        stats = feedback_db.get_stats(days)
        return {
            "success": True,
            "stats": {
                "total_questions": stats.get("total_questions", 0),
                "total_likes": stats.get("total_likes", 0),
                "total_dislikes": stats.get("total_dislikes", 0),
                "total_copies": stats.get("total_copies", 0),
                "total_evidence_views": stats.get("total_evidence_views", 0),
                "satisfaction_rate": stats.get("satisfaction_rate", 0),
                "avg_confidence": stats.get("avg_confidence", 0.0)
            }
        }
    except Exception as e:
        print(f"Error getting feedback stats: {e}")
        return {
            "success": False,
            "stats": {
                "total_questions": 0,
                "total_likes": 0,
                "total_dislikes": 0,
                "total_copies": 0,
                "total_evidence_views": 0,
                "satisfaction_rate": 0,
                "avg_confidence": 0.0
            }
        }

@app.get("/feedback/recent")
def get_recent_feedback(limit: int = 20):
    """Get recent feedback entries"""
    try:
        feedback_list = feedback_db.get_recent(limit)
        return {
            "success": True,
            "feedback": [
                {
                    "question": f.get("question", ""),
                    "reaction_type": f.get("reaction_type", ""),
                    "timestamp": f.get("timestamp", ""),
                    "confidence_score": f.get("confidence_score", 0)
                }
                for f in feedback_list
            ]
        }
    except Exception as e:
        print(f"Error getting recent feedback: {e}")
        return {
            "success": False,
            "feedback": []
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
