#!/usr/bin/env python3
"""
Feedback Database System
Stores user reactions and feedback for chat responses
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import os

class FeedbackDB:
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the feedback database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                reaction_type TEXT NOT NULL,  -- 'like', 'dislike', 'copy', 'view_evidence'
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_session TEXT,
                sources TEXT,  -- JSON array of sources
                evidence_count INTEGER,
                confidence_score REAL,
                additional_data TEXT  -- JSON for extra data
            )
        ''')
        
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
        
        conn.commit()
        conn.close()
        print("Feedback database initialized successfully")
    
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
        """Record user feedback/reaction"""
        
        feedback_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        # Update daily analytics
        today = datetime.now().date()
        cursor.execute('''
            INSERT OR IGNORE INTO analytics (date) VALUES (?)
        ''', (today,))
        
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
        
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_feedback_stats(self, days: int = 7) -> Dict:
        """Get feedback statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(total_questions) as total_questions,
                SUM(total_likes) as total_likes,
                SUM(total_dislikes) as total_dislikes,
                SUM(total_copies) as total_copies,
                SUM(total_evidence_views) as total_evidence_views,
                AVG(avg_confidence) as avg_confidence
            FROM analytics 
            WHERE date >= date('now', '-{} days')
        '''.format(days))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_questions': result[0] or 0,
                'total_likes': result[1] or 0,
                'total_dislikes': result[2] or 0,
                'total_copies': result[3] or 0,
                'total_evidence_views': result[4] or 0,
                'avg_confidence': round(result[5] or 0.0, 3),
                'satisfaction_rate': round((result[1] or 0) / max((result[1] or 0) + (result[2] or 0), 1) * 100, 1)
            }
        
        return {
            'total_questions': 0,
            'total_likes': 0,
            'total_dislikes': 0,
            'total_copies': 0,
            'total_evidence_views': 0,
            'avg_confidence': 0.0,
            'satisfaction_rate': 0.0
        }
    
    def get_recent_feedback(self, limit: int = 50) -> List[Dict]:
        """Get recent feedback entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, message_id, question, reaction_type, timestamp, 
                   sources, evidence_count, confidence_score
            FROM feedback 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        feedback_list = []
        for row in results:
            feedback_list.append({
                'id': row[0],
                'message_id': row[1],
                'question': row[2],
                'reaction_type': row[3],
                'timestamp': row[4],
                'sources': json.loads(row[5]) if row[5] else [],
                'evidence_count': row[6],
                'confidence_score': row[7]
            })
        
        return feedback_list
    
    def record_question(self, user_session: str = None):
        """Record that a question was asked"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update user session
        if user_session:
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions (
                    session_id, last_activity, total_questions
                ) VALUES (
                    ?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT total_questions FROM user_sessions WHERE session_id = ?), 0) + 1
                )
            ''', (user_session, user_session))
        
        # Update daily analytics
        today = datetime.now().date()
        cursor.execute('''
            INSERT OR IGNORE INTO analytics (date) VALUES (?)
        ''', (today,))
        
        cursor.execute('''
            UPDATE analytics SET total_questions = total_questions + 1, updated_at = CURRENT_TIMESTAMP 
            WHERE date = ?
        ''', (today,))
        
        conn.commit()
        conn.close()

# Global feedback database instance
feedback_db = FeedbackDB()