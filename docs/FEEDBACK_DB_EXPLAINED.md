# feedback_db.py - Line-by-Line Explanation

**What is this file?**  
This file manages user feedback and analytics. Think of it like a notebook that records what users think about the AI's answers.

---

## Complete Code with Explanations (Part 1)

```python
#!/usr/bin/env python3
```
**Line 1**: Shebang line. Tells the system to run this file with Python 3.

```python
"""
Feedback Database System
Stores user reactions and feedback for chat responses
"""
```
**Lines 2-4**: Documentation explaining what this file does.

```python
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import os
```
**Lines 6-11**: Import libraries.
- `sqlite3`: Database library
- `json`: Convert data to/from JSON format
- `uuid`: Generate unique IDs
- `datetime`: Work with dates and times
- `Dict, List, Optional`: Type hints
- `os`: Operating system functions

---

## Class: FeedbackDB

```python
class FeedbackDB:
```
**Line 13**: Define a class called FeedbackDB.
- A class is like a blueprint for creating objects

```python
    def __init__(self, db_path: str = "feedback.db"):
```
**Line 14**: Define the constructor (initialization function).
- `db_path: str = "feedback.db"`: The path to the database file (default is "feedback.db")

```python
        self.db_path = db_path
        self.init_database()
```
**Lines 15-16**: Set up the database.
- `self.db_path = db_path`: Store the database path
- `self.init_database()`: Initialize the database

---

## Method: init_database()

```python
    def init_database(self):
```
**Line 18**: Define a method that initializes the database.

```python
        """Initialize the feedback database with required tables"""
```
**Line 19**: Documentation explaining what this method does.

```python
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
```
**Lines 20-21**: Connect to the database.
- `sqlite3.connect()`: Open a connection to the database
- `conn.cursor()`: Create a cursor (like a pen) to write to the database

```python
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                reaction_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_session TEXT,
                sources TEXT,
                evidence_count INTEGER,
                confidence_score REAL,
                additional_data TEXT
            )
        ''')
```
**Lines 23-38**: Create the feedback table.
- `CREATE TABLE IF NOT EXISTS`: Create a table if it doesn't exist
- `id TEXT PRIMARY KEY`: Unique identifier for each feedback
- `message_id TEXT NOT NULL`: ID of the message being reviewed
- `question TEXT NOT NULL`: The question asked
- `answer TEXT NOT NULL`: The answer given
- `reaction_type TEXT NOT NULL`: Type of reaction (like, dislike, copy, view_evidence)
- `timestamp DATETIME DEFAULT CURRENT_TIMESTAMP`: When the feedback was recorded
- `user_session TEXT`: Which user session this came from
- `sources TEXT`: Sources used for the answer
- `evidence_count INTEGER`: How many pieces of evidence
- `confidence_score REAL`: How confident the answer is
- `additional_data TEXT`: Extra data in JSON format

```python
        # Create user sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_questions INTEGER DEFAULT 0,
                total_reactions INTEGER DEFAULT 0
            )
        ''')
```
**Lines 40-48**: Create the user sessions table.
- `session_id TEXT PRIMARY KEY`: Unique ID for each user session
- `created_at DATETIME DEFAULT CURRENT_TIMESTAMP`: When the session started
- `last_activity DATETIME DEFAULT CURRENT_TIMESTAMP`: When the user last did something
- `total_questions INTEGER DEFAULT 0`: How many questions asked
- `total_reactions INTEGER DEFAULT 0`: How many reactions given

```python
        # Create analytics table for aggregated data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_questions INTEGER DEFAULT 0,
                total_likes INTEGER DEFAULT 0,
                total_dislikes INTEGER DEFAULT 0,
                total_copies INTEGER DEFAULT 0,
                total_evidence_views INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0.0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
```
**Lines 50-62**: Create the analytics table.
- `id INTEGER PRIMARY KEY AUTOINCREMENT`: Auto-incrementing ID
- `date DATE DEFAULT CURRENT_DATE`: The date of the analytics
- `total_questions INTEGER DEFAULT 0`: Total questions asked
- `total_likes INTEGER DEFAULT 0`: Total likes
- `total_dislikes INTEGER DEFAULT 0`: Total dislikes
- `total_copies INTEGER DEFAULT 0`: Total times copied
- `total_evidence_views INTEGER DEFAULT 0`: Total times evidence viewed
- `avg_confidence REAL DEFAULT 0.0`: Average confidence score
- `updated_at DATETIME DEFAULT CURRENT_TIMESTAMP`: When updated

```python
        conn.commit()
        conn.close()
        print("Feedback database initialized successfully")
```
**Lines 64-66**: Save and close the database.
- `conn.commit()`: Save all changes
- `conn.close()`: Close the connection
- `print()`: Show a success message

---

## Method: record_feedback()

```python
    def record_feedback(self, 
                       message_id: str,
                       question: str,
                       answer: str,
                       reaction_type: str,
                       user_session: str = None,
                       sources: List[str] = None,
                       evidence_count: int = 0,
                       confidence_score: float = 0.0,
                       additional_data: Dict = None) -> str:
```
**Lines 68-77**: Define a method that records user feedback.
- Takes many parameters about the feedback
- Returns a feedback ID (string)

```python
        """Record user feedback/reaction"""
```
**Line 78**: Documentation explaining what this method does.

```python
        feedback_id = str(uuid.uuid4())
```
**Line 80**: Generate a unique ID for this feedback.
- `uuid.uuid4()`: Generate a random unique ID
- `str()`: Convert it to a string

```python
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
```
**Lines 82-83**: Connect to the database.

```python
        cursor.execute('''
            INSERT INTO feedback (
                id, message_id, question, answer, reaction_type, 
                user_session, sources, evidence_count, confidence_score, additional_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_id,
            message_id,
            question,
            answer,
            reaction_type,
            user_session or str(uuid.uuid4()),
            json.dumps(sources or []),
            evidence_count,
            confidence_score,
            json.dumps(additional_data or {})
        ))
```
**Lines 85-101**: Insert feedback into the database.
- `INSERT INTO feedback`: Add a new row to the feedback table
- `VALUES (?, ?, ...)`: The values to insert (? are placeholders)
- The tuple at the end provides the actual values
- `json.dumps()`: Convert lists/dicts to JSON strings

```python
        # Update user session
        if user_session:
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions (
                    session_id, last_activity, total_reactions
                ) VALUES (
                    ?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT total_reactions FROM user_sessions WHERE session_id = ?), 0) + 1
                )
            ''', (user_session, user_session))
```
**Lines 103-112**: Update the user session.
- `if user_session`: If a session ID was provided
- `INSERT OR REPLACE`: Insert or update if exists
- `COALESCE()`: Use the existing count or 0 if not found
- Increment the total reactions count

```python
        # Update daily analytics
        today = datetime.now().date()
        cursor.execute('''
            INSERT OR IGNORE INTO analytics (date) VALUES (?)
        ''', (today,))
```
**Lines 114-118**: Create an analytics entry for today if it doesn't exist.
- `datetime.now().date()`: Get today's date
- `INSERT OR IGNORE`: Insert only if it doesn't exist

```python
        if reaction_type == 'like':
            cursor.execute('''
                UPDATE analytics SET total_likes = total_likes + 1, updated_at = CURRENT_TIMESTAMP 
                WHERE date = ?
            ''', (today,))
        elif reaction_type == 'dislike':
            cursor.execute('''
                UPDATE analytics SET total_dislikes = total_dislikes + 1, updated_at = CURRENT_TIMESTAMP 
                WHERE date = ?
            ''', (today,))
        elif reaction_type == 'copy':
            cursor.execute('''
                UPDATE analytics SET total_copies = total_copies + 1, updated_at = CURRENT_TIMESTAMP 
                WHERE date = ?
            ''', (today,))
        elif reaction_type == 'view_evidence':
            cursor.execute('''
                UPDATE analytics SET total_evidence_views = total_evidence_views + 1, updated_at = CURRENT_TIMESTAMP 
                WHERE date = ?
            ''', (today,))
```
**Lines 120-141**: Update analytics based on reaction type.
- Check which type of reaction it is
- Increment the corresponding counter
- Update the timestamp

```python
        conn.commit()
        conn.close()
        
        return feedback_id
```
**Lines 143-146**: Save changes and return the feedback ID.

---

## What This File Does (Summary)

1. **Creates tables** - Sets up database structure for feedback, sessions, and analytics
2. **Records feedback** - Stores user reactions and comments
3. **Tracks sessions** - Keeps track of user sessions
4. **Updates analytics** - Maintains daily statistics

## How It's Used

Other files call these methods to:
- Record when users like/dislike answers
- Track user sessions
- Generate analytics reports
- Analyze user feedback

## Simple Analogy

Imagine a survey system:
- **Feedback table** = Individual survey responses
- **User sessions table** = Information about each survey taker
- **Analytics table** = Summary statistics

## Database Structure

```
feedback.db
├── feedback table
│   ├── id (unique ID)
│   ├── message_id (which message)
│   ├── question (what was asked)
│   ├── answer (what was answered)
│   ├── reaction_type (like/dislike/copy/view_evidence)
│   └── ... (other fields)
│
├── user_sessions table
│   ├── session_id (unique session)
│   ├── created_at (when started)
│   ├── total_questions (how many asked)
│   └── total_reactions (how many reactions)
│
└── analytics table
    ├── date (which day)
    ├── total_likes (total likes)
    ├── total_dislikes (total dislikes)
    ├── total_copies (total copies)
    └── ... (other stats)
```

---

**Total Lines**: 146+ (continues with more methods)  
**Complexity**: ⭐⭐ Medium  
**Purpose**: Store and manage user feedback and analytics
