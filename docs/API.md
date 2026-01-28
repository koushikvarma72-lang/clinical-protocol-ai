# Clinical Protocol AI - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required for local development.

## Endpoints

### Health Check
```http
GET /health
```
**Description**: Check if the backend service is running.

**Response**:
```json
{
  "status": "healthy",
  "message": "Backend is running"
}
```

### Upload PDF Document
```http
POST /upload-pdf
```
**Description**: Upload and process a clinical protocol PDF document.

**Request**:
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response**:
```json
{
  "message": "PDF uploaded and processed successfully",
  "filename": "protocol.pdf",
  "pages": 126,
  "chunks": 296,
  "processing_time": 45.2
}
```

### Ask Question (Chat)
```http
POST /ask
```
**Description**: Ask questions about the uploaded protocol document.

**Request**:
```json
{
  "question": "What are the inclusion criteria for this study?"
}
```

**Response**:
```json
{
  "question": "What are the inclusion criteria for this study?",
  "answer": "Here are the key requirements for participants to join this study: Participants must be adults aged 18-65 years with confirmed diagnosis...",
  "sources": ["Page 15", "Page 16", "Page 17"],
  "evidence": [
    {
      "text": "Inclusion criteria text...",
      "page_number": 15,
      "relevance_score": 0.85
    }
  ]
}
```

### Extract Key Sections
```http
GET /extract-key-sections
```
**Description**: Automatically extract key sections from the protocol document.

**Response**:
```json
{
  "sections": [
    {
      "title": "Primary Objective",
      "description": "Main goal and purpose of the clinical trial",
      "content": "The primary objective is to evaluate...",
      "confidence": 0.92,
      "approved": false,
      "sources": ["Page 8", "Page 9"],
      "evidence_count": 4
    }
  ]
}
```

### Review Sections (Generate Summary)
```http
POST /review-sections
```
**Description**: Submit reviewed sections and generate executive summary.

**Request**:
```json
{
  "sections": [
    {
      "title": "Primary Objective",
      "content": "Content here...",
      "approved": true,
      "confidence": 0.92
    }
  ]
}
```

**Response**:
```json
{
  "message": "Review completed successfully",
  "approved_sections_count": 3,
  "final_summary": "# CLINICAL PROTOCOL EXECUTIVE SUMMARY\n\n## STUDY OVERVIEW\n\nThis is a Phase I clinical trial..."
}
```

### Submit Feedback
```http
POST /feedback
```
**Description**: Submit user feedback for analytics.

**Request**:
```json
{
  "message_id": "msg_123",
  "question": "What drug is being tested?",
  "answer": "TAK-653 is being tested...",
  "reaction_type": "like",
  "user_session": "session_456",
  "sources": ["Page 10"],
  "evidence_count": 2,
  "confidence_score": 0.85
}
```

**Response**:
```json
{
  "message": "Feedback recorded successfully",
  "feedback_id": "fb_789"
}
```

### Get System Status
```http
GET /status
```
**Description**: Get current system status and document information.

**Response**:
```json
{
  "status": "ready",
  "vector_count": 296,
  "document_loaded": true,
  "model_ready": true,
  "last_upload": "2026-01-28T10:30:00Z"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

**Error Response Format**:
```json
{
  "error": "Error description",
  "detail": "Detailed error message"
}
```

## Rate Limiting

Currently, no rate limiting is implemented for local development.

## Examples

### Python Example
```python
import requests

# Upload PDF
with open('protocol.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-pdf',
        files={'file': f}
    )

# Ask question
response = requests.post(
    'http://localhost:8000/ask',
    json={'question': 'What is the primary endpoint?'}
)
print(response.json()['answer'])
```

### JavaScript Example
```javascript
// Ask question
const response = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What are the safety measures?'
  })
});

const data = await response.json();
console.log(data.answer);
```

### cURL Example
```bash
# Upload PDF
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@protocol.pdf"

# Ask question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What drug is being tested?"}'
```

## WebSocket Support

Currently, the API uses HTTP requests. WebSocket support for real-time updates is planned for future versions.

## Versioning

The API is currently unversioned. Future versions will include version numbers in the URL path (e.g., `/v1/ask`).