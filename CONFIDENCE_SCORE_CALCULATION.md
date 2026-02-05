# How Confidence Score is Calculated

## Overview

Your system calculates confidence scores at **two different stages**:

1. **Retrieval Confidence** - When searching for relevant document chunks
2. **Extraction Confidence** - When extracting key sections from the protocol

---

## Stage 1: Retrieval Confidence (Vector Search)

### Location
**File:** `backend/new_rag_system.py`  
**Function:** `_find_relevant_sections()`

### Formula

```python
# Calculate relevance score from vector distance
max_distance = 1.2
relevance_score = max(0, (max_distance - distance) / max_distance)
```

### How It Works

1. **Vector Distance Calculation**
   - Your question is converted to a vector embedding
   - Each document chunk is already a vector embedding
   - Cosine distance is calculated between them (0 = identical, 1.2 = very different)

2. **Relevance Score Conversion**
   - Distance is converted to a relevance score (0-1)
   - Formula: `(1.2 - distance) / 1.2`
   - Example:
     - Distance 0.0 → Score 1.0 (perfect match)
     - Distance 0.6 → Score 0.5 (moderate match)
     - Distance 1.2 → Score 0.0 (no match)

3. **Filtering**
   - Only chunks with relevance_score > 0.2 are kept
   - Administrative content is filtered out
   - Top 6 most relevant chunks are returned

### Example

```
Question: "What are the inclusion criteria?"

Chunk 1: "Participants must be 18-65 years old..."
  Distance: 0.3
  Relevance Score: (1.2 - 0.3) / 1.2 = 0.75 ✅ KEPT

Chunk 2: "Table of Contents..."
  Distance: 1.1
  Relevance Score: (1.2 - 1.1) / 1.2 = 0.08 ❌ FILTERED OUT

Chunk 3: "Inclusion criteria include..."
  Distance: 0.1
  Relevance Score: (1.2 - 0.1) / 1.2 = 0.92 ✅ KEPT (TOP)
```

---

## Stage 2: Extraction Confidence (Key Sections)

### Location
**File:** `backend/main.py`  
**Function:** `extract_key_sections()`

### Formula

```python
# Base confidence
base_confidence = 0.7

# Bonus for multiple sources
source_bonus = min(0.2, len(sources) * 0.04)
# Each source adds 4%, max 20%

# Bonus for evidence
evidence_bonus = min(0.1, len(evidence) * 0.02)
# Each evidence adds 2%, max 10%

# Final confidence (capped at 0.95)
confidence = min(0.95, base_confidence + source_bonus + evidence_bonus)
```

### How It Works

1. **Base Confidence: 0.7 (70%)**
   - Every extracted section starts at 70% confidence
   - This is the baseline for AI-generated content

2. **Source Bonus: +0% to +20%**
   - Each source (page reference) adds 4%
   - Maximum 5 sources = 20% bonus
   - Formula: `min(0.2, len(sources) * 0.04)`
   - Examples:
     - 1 source → +0.04 (4%)
     - 3 sources → +0.12 (12%)
     - 5+ sources → +0.20 (20%)

3. **Evidence Bonus: +0% to +10%**
   - Each evidence chunk adds 2%
   - Maximum 5 evidence chunks = 10% bonus
   - Formula: `min(0.1, len(evidence) * 0.02)`
   - Examples:
     - 1 evidence → +0.02 (2%)
     - 3 evidence → +0.06 (6%)
     - 5+ evidence → +0.10 (10%)

4. **Final Confidence (Capped at 95%)**
   - Total cannot exceed 0.95 (95%)
   - Formula: `min(0.95, base_confidence + source_bonus + evidence_bonus)`

### Examples

**Example 1: Low Confidence**
```
Base Confidence:    0.70 (70%)
Sources:            1 page → +0.04 (4%)
Evidence:           1 chunk → +0.02 (2%)
─────────────────────────────
Total Confidence:   0.76 (76%)
```

**Example 2: Medium Confidence**
```
Base Confidence:    0.70 (70%)
Sources:            3 pages → +0.12 (12%)
Evidence:           3 chunks → +0.06 (6%)
─────────────────────────────
Total Confidence:   0.88 (88%)
```

**Example 3: High Confidence**
```
Base Confidence:    0.70 (70%)
Sources:            5 pages → +0.20 (20%)
Evidence:           5 chunks → +0.10 (10%)
─────────────────────────────
Total Confidence:   0.95 (95%) [CAPPED]
```

---

## Stage 3: Query Response Confidence

### Location
**File:** `backend/new_rag_system.py`  
**Function:** `_find_relevant_sections()`

### Calculation

```python
# Confidence based on top result's relevance score
confidence = 1 - results['distances'][0][0]
```

### How It Works

1. **Distance to Confidence Conversion**
   - Takes the distance of the most relevant chunk
   - Converts to confidence: `1 - distance`
   - Range: 0 to 1 (0% to 100%)

2. **Examples**
   - Distance 0.0 → Confidence 1.0 (100%)
   - Distance 0.2 → Confidence 0.8 (80%)
   - Distance 0.5 → Confidence 0.5 (50%)
   - Distance 1.0 → Confidence 0.0 (0%)

---

## Stage 4: Feedback Confidence Tracking

### Location
**File:** `backend/feedback_db.py`  
**Function:** `record_feedback()`

### What's Tracked

```python
# Stored in feedback database
confidence_score: float  # The confidence of the answer

# Used for analytics
avg_confidence: float    # Average confidence across all feedback
```

### How It's Used

1. **Recording Feedback**
   - When user provides feedback (like/dislike/copy/view evidence)
   - The confidence score of that answer is recorded
   - Stored in SQLite feedback table

2. **Analytics Calculation**
   - Average confidence is calculated across all feedback
   - Used in dashboard to show overall system performance
   - Helps identify which types of questions have lower confidence

---

## Complete Flow: Question to Confidence

### Step 1: User Asks Question
```
User: "What are the inclusion criteria?"
```

### Step 2: Vector Search
```
Question → Embedding → Search Chroma DB
↓
Find relevant chunks with distances
↓
Calculate relevance scores: (1.2 - distance) / 1.2
↓
Filter chunks with score > 0.2
↓
Return top 6 chunks with scores
```

### Step 3: LLM Reads Chunks
```
LLM reads top 4 chunks
↓
Generates answer based on context
↓
Returns answer with sources and evidence
```

### Step 4: Calculate Extraction Confidence
```
Base: 0.70
+ Source Bonus: len(sources) * 0.04 (max 0.2)
+ Evidence Bonus: len(evidence) * 0.02 (max 0.1)
= Final Confidence (max 0.95)
```

### Step 5: Return to User
```
{
  "answer": "The inclusion criteria are...",
  "sources": ["Page 5", "Page 12", "Page 18"],
  "evidence": [chunk1, chunk2, chunk3],
  "confidence": 0.88  ← Calculated confidence
}
```

### Step 6: User Provides Feedback
```
User clicks "👍 Like"
↓
Feedback recorded with confidence_score: 0.88
↓
Analytics updated
↓
Dashboard shows average confidence
```

---

## Confidence Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 0.95+ | Excellent | Trust the answer |
| 0.85-0.94 | Very Good | Generally reliable |
| 0.75-0.84 | Good | Mostly accurate |
| 0.65-0.74 | Fair | Review carefully |
| 0.50-0.64 | Low | Verify with source |
| < 0.50 | Very Low | Manual review needed |

---

## Factors Affecting Confidence

### Increases Confidence ✅
- Multiple sources (pages) mentioning the topic
- Multiple evidence chunks supporting the answer
- High relevance scores from vector search
- Clear, specific information in the protocol

### Decreases Confidence ❌
- Single source for the answer
- Limited evidence chunks
- Low relevance scores from vector search
- Ambiguous or vague information
- Administrative content filtered out

---

## Real-World Example

### Scenario: Extract "Primary Objective"

**Step 1: Search**
```
Question: "What is the primary objective of this study?"
↓
Vector search finds:
- Chunk A (Distance 0.15): "Primary objective is to evaluate safety..."
- Chunk B (Distance 0.25): "Study aims to determine..."
- Chunk C (Distance 0.35): "Objective includes..."
↓
Relevance scores:
- Chunk A: (1.2 - 0.15) / 1.2 = 0.875
- Chunk B: (1.2 - 0.25) / 1.2 = 0.792
- Chunk C: (1.2 - 0.35) / 1.2 = 0.708
```

**Step 2: LLM Processing**
```
LLM reads top 3 chunks
↓
Generates: "The primary objective is to evaluate the safety and 
tolerability of TAK-653 in healthy volunteers."
↓
Sources: ["Page 5", "Page 12"]
Evidence: [chunk_A, chunk_B, chunk_C]
```

**Step 3: Calculate Confidence**
```
Base Confidence:        0.70
Sources (2 pages):      2 * 0.04 = 0.08
Evidence (3 chunks):    3 * 0.02 = 0.06
─────────────────────────────
Total:                  0.70 + 0.08 + 0.06 = 0.84
```

**Step 4: Return to User**
```
{
  "title": "Primary Objective",
  "content": "The primary objective is to evaluate...",
  "confidence": 0.84,  ← 84% confidence
  "sources": ["Page 5", "Page 12"],
  "evidence_count": 3
}
```

---

## Confidence in Dashboard

### What You See
```
Feedback Dashboard
├── Total Questions: 45
├── Positive Reactions: 38
├── Satisfaction Rate: 84%
└── Average AI Confidence Score: 0.87 (87%)
```

### How It's Calculated
```
Average Confidence = Sum of all confidence_scores / Total feedback entries

Example:
- Answer 1: 0.88
- Answer 2: 0.92
- Answer 3: 0.81
- Answer 4: 0.85
─────────────────
Average: (0.88 + 0.92 + 0.81 + 0.85) / 4 = 0.865 ≈ 0.87
```

---

## Improving Confidence Scores

### For Better Retrieval Confidence
1. Upload high-quality PDFs with clear text
2. Ensure PDFs are not scanned images
3. Use specific, detailed questions
4. Ask about topics explicitly mentioned in the protocol

### For Better Extraction Confidence
1. Ensure multiple pages mention the topic
2. Use well-structured protocols
3. Provide clear, unambiguous information
4. Avoid administrative content

### For Better Overall Confidence
1. Provide feedback (like/dislike) to train the system
2. Review low-confidence answers manually
3. Provide corrections for inaccurate answers
4. Use the system consistently

---

## Technical Details

### Confidence Score Range
- **Minimum:** 0.0 (0%)
- **Maximum:** 0.95 (95%)
- **Default Base:** 0.70 (70%)

### Calculation Precision
- Rounded to 2 decimal places
- Example: 0.8765 → 0.88

### Storage
- Stored in SQLite feedback table
- Used for analytics and dashboard
- Tracked over time for performance monitoring

---

## Summary

Your confidence score is calculated through a **multi-stage process**:

1. **Retrieval Stage:** Vector distance → Relevance score (0-1)
2. **Extraction Stage:** Base (0.7) + Source bonus (0-0.2) + Evidence bonus (0-0.1) = Final (max 0.95)
3. **Feedback Stage:** Confidence recorded and averaged for analytics
4. **Dashboard Stage:** Average confidence displayed to users

**Key Formula:**
```
Confidence = min(0.95, 0.70 + (sources * 0.04) + (evidence * 0.02))
```

This ensures your system provides **transparent, explainable confidence scores** that reflect the quality and reliability of each answer.

---

**Last Updated:** February 5, 2026  
**Status:** ✅ Complete Explanation
