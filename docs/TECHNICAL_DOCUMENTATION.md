# Clinical Protocol AI - Technical Documentation

## Table of Contents

1. [System Overview & Architecture](#system-overview--architecture)
2. [Document Processing Pipeline](#document-processing-pipeline)
3. [Query Processing & Answer Generation](#query-processing--answer-generation)
4. [Core Features & Capabilities](#core-features--capabilities)
5. [System Requirements, Deployment & Security](#system-requirements-deployment--security)
6. [API Reference & Integration](#api-reference--integration)
7. [User Workflows & Use Cases](#user-workflows--use-cases)

---

## Executive Summary

Clinical Protocol AI is an AI-powered system designed to support the analysis, interpretation, and review of clinical trial protocol documents. By combining advanced document processing, semantic search, and large language models, the platform transforms static protocol PDFs into interactive, searchable, and intelligent knowledge sources. This documentation provides a comprehensive technical overview of the system's architecture, capabilities, deployment options, and integration patterns.

---

## System Overview & Architecture

### What is Clinical Protocol AI?

Clinical Protocol AI is an AI-powered system designed to support the analysis, interpretation, and review of clinical trial protocol documents. Clinical trial protocols are often lengthy, complex, and highly structured, making manual review time-consuming and error-prone. This system assists teams by transforming static protocol PDFs into an interactive, searchable, and intelligent knowledge source.

The primary use case is the analysis of clinical trial protocols, including eligibility criteria, study design, endpoints, safety monitoring, and procedural schedules. Instead of manually searching through hundreds of pages, users can ask natural-language questions and receive precise, context-aware answers grounded directly in the source document.

Clinical Protocol AI is intended for clinical researchers, medical writers, regulatory affairs teams, clinical operations staff, and quality reviewers who need fast and reliable access to protocol insights while maintaining traceability to the original document.

### Core Architecture

The system follows a modular, service-oriented architecture that separates document processing, data storage, and user interaction. At a high level, the workflow begins when a user uploads a clinical protocol document and ends with interactive, citation-backed answers delivered through a web interface.

The backend, built using Python and FastAPI, manages all core intelligence tasks including document ingestion, text processing, embedding generation, and query orchestration. The frontend, developed in React, provides an intuitive user interface for uploading documents, tracking processing status, and interacting with the AI assistant. A vector database (ChromaDB) stores semantic representations of protocol content, enabling efficient retrieval during question answering.

**Data flow overview:**

```
Document Upload → Text Extraction & Chunking → Embedding Generation → Vector Storage → User Query → Context Retrieval → AI Answer Generation
```

### Key Technologies

The backend is implemented using FastAPI, chosen for its high performance, asynchronous support, and clean API design. ChromaDB serves as the vector database, storing embeddings that represent protocol content in a searchable semantic space. Large language model inference is handled using Llama 3.1 running locally via Ollama, ensuring data privacy and offline capability.

The frontend is built with React and Material-UI, providing a responsive and consistent user experience. Communication between the frontend and backend occurs through RESTful APIs, enabling clear separation of concerns and easy extensibility.

### System Capabilities

Clinical Protocol AI provides multiple high-value capabilities tailored to clinical workflows. The system performs automated document analysis and structured section extraction, enabling quick access to critical protocol components. Users can interact with the protocol through conversational Q&A, receiving answers grounded in the original text.

In addition, the platform supports executive summary generation to assist stakeholders who require high-level insights rather than full document review. Real-time progress tracking informs users about document processing stages, improving transparency and usability during large or complex uploads.

Together, these capabilities transform traditional protocol review into an efficient, AI-assisted workflow while maintaining accuracy, traceability, and user control.

---

## Document Processing Pipeline

### PDF Ingestion & Text Extraction

The document processing pipeline begins when a user uploads a clinical trial protocol PDF through the web interface. The frontend transmits the file securely to the backend via a RESTful API, where it is validated and registered for processing. Once accepted, the document enters an automated ingestion workflow managed by the backend service.

During text extraction, the system parses the PDF page by page rather than treating it as a single block of text. This approach allows preservation of page-level metadata, including page numbers and document order, which is essential for traceability and audit review. Each extracted text segment retains a reference to its original page location, enabling downstream answers to be linked back to the source document.

Clinical protocols often contain complex structures such as tables, multi-level headings, numbered sections, and procedural schedules. The extraction process is designed to handle these variations by normalizing text while preserving logical structure. This ensures that important contextual cues—such as section boundaries or eligibility lists—are not lost during conversion from PDF to machine-readable text.

### Text Chunking Strategy

Clinical protocol documents are not processed as a single continuous text. Large documents exceed the effective context limits of language models and reduce retrieval precision. To address this, the system divides extracted text into smaller, manageable segments known as chunks.

Chunking improves both accuracy and efficiency. Each chunk represents a focused portion of the protocol—such as a subsection or paragraph group—allowing the system to retrieve only the most relevant content during question answering. To prevent loss of meaning, chunks are created with controlled overlap, ensuring that important context spanning multiple paragraphs remains intact.

Every chunk is enriched with metadata, including source page number, chunk index, and relative position within the document. This metadata plays a critical role later in retrieval, citation, and answer explanation, enabling users to understand exactly where information originated.

### Embedding Generation

Once chunked, each text segment is transformed into an embedding. An embedding is a numerical representation of text that captures its semantic meaning rather than its exact wording. In simple terms, embeddings allow the system to understand what a passage is about, not just which words it contains.

This process can be compared to organizing a library by subject instead of alphabet. Two chunks discussing eligibility criteria may be stored close together in meaning, even if they use different terminology. The embedding model converts each chunk into a high-dimensional vector that encodes these relationships.

By representing text in this semantic form, the system enables intelligent search based on meaning, similarity, and intent rather than exact keyword matching.

### Vector Database Storage

All generated embeddings are stored in ChromaDB, which functions as a vector database optimized for similarity search. Unlike traditional databases that rely on exact matches, a vector database retrieves content based on how semantically close two pieces of text are.

When a user submits a question, the system generates an embedding for the query and rapidly compares it against stored vectors. ChromaDB identifies the most relevant chunks within milliseconds, even across large documents.

This mechanism enables fast, accurate retrieval of protocol sections and forms the foundation of the Retrieval-Augmented Generation workflow. In effect, ChromaDB acts like a highly intelligent index—similar to a library catalog system, but organized by meaning rather than keywords—ensuring that subsequent AI responses are grounded in the most relevant source material.

---

## Query Processing & Answer Generation

### User Query Submission

Users interact with Clinical Protocol AI through a conversational chat interface on the frontend. Questions can be asked in natural language, such as inquiries about eligibility criteria, visit schedules, endpoints, or safety procedures. The interface is designed to feel intuitive, allowing users to explore protocol content without requiring technical or query-specific syntax.

Once a question is submitted, the backend performs basic validation and preprocessing. This includes trimming irrelevant characters, normalizing text, and ensuring the query meets minimum content requirements. The system may also apply lightweight query expansion, where related terms or clinical synonyms are considered during retrieval. This improves recall when users phrase questions differently from the wording used in the protocol document.

### Semantic Search & Retrieval

After preprocessing, the user's question is converted into an embedding using the same Llama-based embedding model applied during document processing. This ensures both documents and queries exist within the same semantic space, enabling meaningful comparison.

The generated query embedding is then passed to ChromaDB, which performs a similarity search against stored protocol chunk embeddings. Instead of matching keywords, ChromaDB identifies chunks whose meanings are most closely aligned with the user's intent.

Each candidate result receives a relevance score based on semantic similarity. Low-confidence matches are filtered out, and only the most relevant results are retained. Typically, the system retrieves the top-k chunks, often between 3 and 6, balancing completeness with clarity. Retrieving too few chunks risks missing context, while too many can dilute answer quality.

This retrieval step ensures that only the most relevant portions of the protocol are forwarded for answer generation.

### Context Assembly

The retrieved chunks are then organized into a structured context package. Chunks are ordered logically—often by relevance and original document position—to preserve readability and narrative flow.

Each chunk includes its associated metadata, such as page number, chunk identifier, and source reference. This metadata is not only retained internally but also used later for citation and traceability.

Before being sent to the language model, the context is formatted into a clear, structured prompt. This prompt instructs the model to rely exclusively on the provided protocol content when generating its response, reinforcing factual grounding and reducing the risk of unsupported statements.

### Answer Generation with LLM

The assembled context is passed to the Llama 3.1 language model running locally via Ollama. The model analyzes the retrieved protocol excerpts and generates a coherent, human-readable answer based strictly on that information.

The LLM synthesizes content across multiple chunks when necessary, producing responses that feel conversational while remaining document-grounded. If the model fails to produce a valid response—due to timeouts, insufficient context, or system constraints—fallback mechanisms return partial answers, clarification prompts, or structured excerpts directly from the source text.

This approach ensures reliability even under suboptimal conditions.

### Response Formatting & Citation

Once an answer is generated, the system attaches source references derived from chunk metadata. Page numbers and document identifiers are included alongside the response, enabling users to immediately trace information back to its original location.

Traceability is essential in clinical and regulatory environments, where every decision must be verifiable. By linking answers directly to protocol pages, the system supports audit readiness, internal review, and regulatory confidence.

Users can cross-check AI-generated responses against the original document, ensuring transparency and trust.

**End-to-end workflow overview:**

```
Question → Embedding → Semantic Search → Top-K Retrieval → Context Assembly → Answer Generation → Citation
```

---

## Core Features & Capabilities

### Interactive Chat Assistant

Clinical Protocol AI provides an interactive chat assistant that allows users to ask natural-language questions directly against the uploaded protocol. Users can query a wide range of topics, including study objectives, inclusion and exclusion criteria, trial design, visit schedules, endpoints, safety monitoring, and investigational product details.

The assistant is designed to respond in clear, professional clinical language, producing answers that feel human-like while remaining precise and factual. In internal evaluations, the system achieves an approximately 80% human-like response success rate, measured by relevance, clarity, and completeness of answers during expert review.

All responses are grounded in retrieved protocol content and accompanied by citations, including page numbers and source references. This ensures that users can immediately verify answers against the original document.

**User benefit:** This enables teams to explore protocols conversationally without sacrificing accuracy or traceability.

### Automated Document Analysis

Beyond question answering, the system performs automated analysis of the protocol to extract key structured sections. Commonly extracted sections include Primary Objective, Inclusion Criteria, Exclusion Criteria, Study Endpoints, Safety Considerations, and Study Drug Information.

Each extracted section is assigned a confidence score reflecting the system's certainty based on source consistency and retrieval strength. Rather than automatically finalizing outputs, the platform supports an interactive review workflow. Users can review each extracted section, approve or reject it, and optionally request refinement before it is used downstream.

This human-in-the-loop design ensures alignment with regulatory expectations and clinical judgment.

**User benefit:** This reduces manual extraction effort while preserving expert control and accountability.

### Executive Summary Generation

Once extracted sections are reviewed and approved, Clinical Protocol AI can generate an executive summary suitable for stakeholder and regulatory review. The summary is compiled exclusively from approved content, ensuring consistency with the source protocol.

The generated summary follows a professional structure, typically covering study overview, objectives, design, eligibility criteria, safety considerations, and investigational product details. Formatting is optimized for clarity and readability, making it suitable for internal decision-making, governance meetings, or briefing documents.

Users can export the summary through multiple options, including download, print-ready format, or direct copy to clipboard for integration into other documentation.

**User benefit:** This accelerates preparation of high-quality summaries without compromising accuracy or compliance.

### Real-Time Progress Tracking

Protocol processing involves multiple stages, which can take time for large or complex documents. The system provides real-time progress tracking across each stage, including file upload, text extraction, chunking, embedding generation, and vector storage.

Users can view percentage completion, the current processing stage, and an estimated time remaining. This transparency reduces uncertainty and improves usability, particularly when handling lengthy protocols.

**User benefit:** This keeps users informed and confident during long-running processing tasks.

### Feedback & Analytics

Clinical Protocol AI continuously captures usage and performance data to support quality improvement. User interactions such as questions asked, answers rated, and sections approved or rejected are tracked in aggregate. Quality metrics, including response relevance and user satisfaction signals, are collected to evaluate system effectiveness.

Operational analytics—such as document processing time, retrieval accuracy, and response latency—are also monitored. These insights are used to refine chunking strategies, retrieval parameters, and prompt design over time.

All analytics are designed to support system improvement without exposing sensitive protocol content.

**User benefit:** This ensures the platform evolves continuously while maintaining compliance, reliability, and user trust.

---

## System Requirements, Deployment & Security

### System Requirements

Clinical Protocol AI is designed to run in both local and enterprise-controlled environments, supporting flexible deployment models. The minimum recommended hardware configuration includes 8–16 GB RAM, a modern multi-core CPU, and at least 20–30 GB of available storage for protocol files, embeddings, and application logs. A GPU is optional but recommended for improved language model inference performance, particularly when processing large documents or handling multiple concurrent users.

The system supports Windows, macOS, and Linux operating systems. Software prerequisites include Python 3.8 or later for backend services, Node.js 16 or later for frontend development and builds, and Ollama for managing and running the Llama 3.1 language model locally.

Network requirements are minimal. The platform can operate entirely within an internal network with no outbound internet access. This enables fully local deployments, while still allowing optional cloud or hybrid deployments when organizational policies permit.

### Deployment Architecture

Clinical Protocol AI supports both development and production deployment scenarios. In development environments, the frontend and backend typically run on a single machine. The React frontend communicates with the FastAPI backend through local REST endpoints, enabling rapid iteration and testing.

For production deployments, containerization using Docker is recommended. The backend can be deployed using FastAPI with a production-grade application server such as Gunicorn or Uvicorn workers. A reverse proxy (e.g., NGINX) may be introduced for TLS termination, routing, and request buffering. For higher user volumes, load balancing can be applied across multiple backend instances.

The frontend is compiled into a static build and can be served via a web server or deployed through a CDN, making it lightweight and easily scalable. ChromaDB persists embeddings to disk, with storage paths configurable to align with organizational data retention policies.

**Deployment flow overview:**

```
Frontend → API Gateway / Reverse Proxy → Backend Services → Vector Database (ChromaDB)
```

### Data Privacy & Security

Data privacy is a core design principle of Clinical Protocol AI. All document processing and AI inference are performed locally using Llama 3.1 executed via Ollama, ensuring that protocol data never leaves the organization's infrastructure.

The system does not rely on external APIs for document parsing, embedding generation, or language model inference. This eliminates the risk of unintended data transmission and supports deployments within restricted or air-gapped environments.

The architecture is HIPAA-ready by design, as documents are processed entirely on local systems or approved internal servers. For additional protection, stored embeddings, extracted metadata, and feedback data can be encrypted at rest using standard file-system or database-level encryption mechanisms.

User authentication and role-based access control can be integrated to restrict document access and administrative functions. While basic access control may be implemented initially, enterprise-grade identity integration (such as SSO or directory-based authentication) is supported as a planned enhancement.

### Scalability Considerations

The system supports both single-document workflows and multi-document environments. For performance optimization, embedding generation and document processing tasks are designed to run in parallel, enabling up to 70% faster analysis compared to sequential processing.

Memory management mechanisms ensure temporary artifacts are released after processing, preventing resource exhaustion during large uploads. The architecture is capable of handling very large protocols, including documents exceeding 1,000 pages, through staged processing and incremental storage.

As usage scales, additional backend workers can be added horizontally, while the vector database continues to support efficient similarity search across growing document collections.

### Monitoring & Maintenance

Clinical Protocol AI includes operational features to support long-term stability. Health-check endpoints provide real-time system status for monitoring tools. Structured error logging enables efficient troubleshooting and root-cause analysis.

Model warm-up procedures reduce initial latency after startup, improving first-response performance. Regular database maintenance tasks—such as cleanup of unused embeddings or deprecated documents—help maintain optimal retrieval performance.

Performance metrics including processing time, retrieval latency, and system load can be monitored to guide tuning and capacity planning. For IT teams, this design provides a maintainable, secure, and deployment-ready platform suitable for regulated clinical environments.

---

## API Reference & Integration

### REST API Overview

Clinical Protocol AI exposes a RESTful API that enables programmatic interaction with all core system capabilities. The API is designed for simplicity, consistency, and ease of integration with internal clinical systems.

The base endpoint typically follows the structure:

```
http://localhost:8000/api
```

All requests and responses use JSON as the standard data format. Authentication can be enabled depending on deployment configuration, commonly using API keys or session-based authentication for internal systems.

The API follows standard HTTP semantics. Successful requests return appropriate 2xx status codes, while client and server errors return structured error responses with meaningful messages.

### Key API Endpoints

#### POST /upload-pdf

**Purpose:** Uploads a clinical protocol PDF and initiates processing (extraction, chunking, embedding).

**Input:**
- Multipart file (PDF)

**Response:**
```json
{
  "task_id": "abc123",
  "status": "processing_started"
}
```

#### POST /chat or /ask-question

**Purpose:** Submits a natural-language question against a processed protocol.

**Input:**
- `question` (string)
- `protocol_id` (optional)

**Response:**
```json
{
  "answer": "The primary objective is to evaluate safety and efficacy.",
  "sources": [
    {
      "page": 12,
      "section": "Study Objectives"
    }
  ]
}
```

#### GET /extract-key-sections

**Purpose:** Triggers automated extraction of structured protocol sections.

**Response:**
```json
{
  "sections": {
    "Inclusion Criteria": {
      "text": "...",
      "confidence": 92
    }
  }
}
```

#### POST /review-sections

**Purpose:** Submits user-approved or rejected sections for executive summary generation.

**Input:**
- Section decisions (approve/reject)

**Response:**
```json
{
  "summary_status": "approved_sections_received"
}
```

#### GET /upload-progress/{task_id}

**Purpose:** Provides real-time processing progress for long-running uploads.

**Response:**
```json
{
  "stage": "embedding_generation",
  "progress_percent": 68,
  "estimated_time_remaining": "2 minutes"
}
```

#### POST /feedback

**Purpose:** Collects user ratings and qualitative feedback.

**Input:**
- `rating` (1–5)
- `optional comment`

**Response:**
```json
{
  "status": "feedback_recorded"
}
```

### Response Format & Error Handling

All API responses follow a consistent JSON structure.

**Success (HTTP 200):**
```json
{
  "status": "success",
  "data": {}
}
```

**Client errors (HTTP 400 / 404):**
```json
{
  "status": "error",
  "message": "Invalid protocol ID"
}
```

**Server errors (HTTP 500):**
```json
{
  "status": "error",
  "message": "Internal processing failure"
}
```

Long-running operations such as document ingestion are handled asynchronously. The API immediately returns a task identifier, allowing clients to poll progress endpoints without blocking.

Rate limiting can be enabled in production environments to protect system stability, particularly for chat-heavy workloads.

### Integration Patterns

Clinical Protocol AI can be integrated with external platforms such as clinical trial management systems (CTMS), document repositories, or internal dashboards.

Common patterns include:

- Synchronous chat integration for real-time protocol Q&A
- Asynchronous batch processing for uploading multiple protocols
- Progress polling using task identifiers
- Data export in JSON, CSV, or generated PDF summaries

Webhook or callback-based notification patterns can be introduced to notify external systems when document processing completes.

### Example Workflows

**Complete workflow:** Upload PDF → Track processing → Ask questions → Extract key sections → Review → Generate executive summary

**Minimal workflow:** Upload PDF → Ask questions only

**Batch workflow:** Upload multiple documents → Monitor progress per task → Query each protocol independently

**Logical flow overview:**

```
Client Application → REST API → Processing Pipeline → Vector Database → Answer Generation → Structured Response
```

These APIs allow Clinical Protocol AI to function both as a standalone application and as an embedded intelligence service within broader clinical and regulatory ecosystems.

---

## User Workflows & Use Cases

### Clinical Research Teams

Clinical research teams frequently need to review new study protocols during study startup, feasibility assessments, or internal alignment meetings. These documents often exceed several hundred pages, making traditional review slow and repetitive.

**Typical workflow:** Upload protocol → Ask targeted questions about study design and endpoints → Generate executive summary for team briefing

Using the chat interface, researchers can immediately query critical elements such as objectives, endpoints, population definition, and overall study structure. Common questions include "What are the inclusion criteria?" or "What is the primary endpoint?"

**Value delivered:** Clinical Protocol AI can reduce initial protocol review time from 4–6 hours to approximately 10–15 minutes, enabling faster study evaluation and earlier decision-making.

### Regulatory Affairs & Compliance

Regulatory teams rely on precise, consistent documentation when preparing submissions and responding to regulatory authorities. Manual extraction of protocol content introduces risk, particularly when content must remain fully traceable.

**Typical workflow:** Upload protocol → Extract key sections → Review and approve content → Generate executive summary for regulatory submission

The automated extraction of objectives, eligibility criteria, endpoints, and safety sections allows regulatory professionals to validate content efficiently. The review-and-approval workflow ensures only confirmed interpretations are included in final documentation.

**Value delivered:** This approach improves consistency, strengthens traceability, and significantly reduces rework during submission preparation. It also supports generation of regulatory briefing documents or CDISC-aligned summaries derived directly from approved protocol content.

### Clinical Operations & Project Management

Clinical operations teams require frequent access to protocol details during site initiation visits, investigator meetings, and ongoing trial execution. Searching manually through lengthy PDFs during meetings is inefficient and disruptive.

**Typical workflow:** Upload protocol → Use chat interface for ad-hoc questions during discussions

Operations staff can ask real-time questions such as "What are the visit windows?" or "Which laboratory assessments are required at baseline?" and receive immediate, cited answers.

**Value delivered:** This enables rapid clarification without interrupting meetings, reducing delays and improving operational alignment across study teams.

### Medical Writing & Documentation

Medical writers routinely extract protocol content for downstream documents such as clinical study reports (CSRs), investigator brochures, and regulatory summaries. Manual transcription increases the risk of inconsistency and version drift.

**Typical workflow:** Upload protocol → Extract structured sections → Export summaries → Integrate into documents

Extracted sections can be reviewed, approved, and exported in structured formats for reuse in writing workflows.

**Value delivered:** This reduces manual transcription effort by 50–70% and improves accuracy by ensuring all content is sourced directly from the protocol with traceable references.

### Quality & Audit Functions

Quality assurance and audit teams require clear documentation trails that demonstrate how protocol understanding was derived and verified. During inspections, teams must show both accuracy and traceability.

**Typical workflow:** Upload protocol → Generate structured summary → Maintain audit log of queries, extractions, and approvals

All interactions—including questions asked, sections extracted, and approvals granted—form a transparent audit trail.

**Value delivered:** This supports internal audits and regulatory inspections, such as FDA reviews, by demonstrating documented protocol interpretation and controlled review processes.

### Multi-Protocol Environments

Organizations managing multiple concurrent trials often need to compare protocols across phases or therapeutic areas. Manual cross-document comparison is particularly time-consuming.

**Typical workflow:** Upload multiple protocols → Query each independently → Compare extracted sections across studies

Teams can compare inclusion criteria, endpoints, or safety requirements across Phase 2 and Phase 3 studies to ensure consistency.

**Value delivered:** This enables cross-protocol analysis in minutes rather than hours, supporting portfolio-level oversight and consistency checks.

---

## Appendix

### Glossary

- **Embedding:** A numerical representation of text that captures semantic meaning, enabling similarity-based search.
- **ChromaDB:** A vector database optimized for storing and retrieving embeddings.
- **Llama 3.1:** A large language model used for natural language understanding and generation.
- **Ollama:** A tool for running large language models locally.
- **RAG (Retrieval-Augmented Generation):** A technique that retrieves relevant context before generating responses, improving accuracy and grounding.
- **Vector Database:** A database optimized for similarity search based on semantic vectors.
- **Chunk:** A segment of text extracted from a document, typically a paragraph or section.
- **Metadata:** Information about a chunk, such as page number and source reference.

### Acronyms

- **API:** Application Programming Interface
- **CDISC:** Clinical Data Interchange Standards Consortium
- **CDN:** Content Delivery Network
- **CORS:** Cross-Origin Resource Sharing
- **CSR:** Clinical Study Report
- **CTMS:** Clinical Trial Management System
- **FDA:** Food and Drug Administration
- **HIPAA:** Health Insurance Portability and Accountability Act
- **JSON:** JavaScript Object Notation
- **LLM:** Large Language Model
- **NGINX:** Nginx Web Server
- **PDF:** Portable Document Format
- **REST:** Representational State Transfer
- **SSO:** Single Sign-On
- **TLS:** Transport Layer Security

---

**Document Version:** 1.0  
**Last Updated:** January 31, 2026  
**Status:** Complete Technical Documentation
