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
                reaction_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_session TEXT,
                sources TEXT,
                evidence_count INTEGER,
                confidence_score REAL,
                additional_data TEXT
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
        
        # Create summary approvals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summary_approvals (
                id TEXT PRIMARY KEY,
                summary_id TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_session TEXT,
                summary_content TEXT,
                approved_sections_count INTEGER
            )
        ''')
        
        # Create documents table to track uploaded documents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                category TEXT,
                pages_count INTEGER,
                chunks_count INTEGER,
                file_size INTEGER,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_session TEXT,
                status TEXT DEFAULT 'completed'
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
    
    def get_stats(self, days: int = 7) -> Dict:
        """Alias for get_feedback_stats for API compatibility"""
        return self.get_feedback_stats(days)
    
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
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Alias for get_recent_feedback for API compatibility"""
        return self.get_recent_feedback(limit)
    
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
    
    def record_summary_approval(self,
                               summary_id: str,
                               status: str,
                               reason: str = None,
                               user_session: str = None,
                               summary_content: str = None,
                               approved_sections_count: int = 0) -> str:
        """Record summary approval or disapproval with reason"""
        
        approval_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO summary_approvals (
                id, summary_id, status, reason, user_session, 
                summary_content, approved_sections_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            approval_id,
            summary_id,
            status,
            reason,
            user_session or str(uuid.uuid4()),
            summary_content,
            approved_sections_count
        ))
        
        conn.commit()
        conn.close()
        
        return approval_id
    
    def get_summary_approvals(self, limit: int = 50) -> List[Dict]:
        """Get recent summary approvals/disapprovals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, summary_id, status, reason, timestamp, 
                   approved_sections_count
            FROM summary_approvals 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        approvals_list = []
        for row in results:
            approvals_list.append({
                'id': row[0],
                'summary_id': row[1],
                'status': row[2],
                'reason': row[3],
                'timestamp': row[4],
                'approved_sections_count': row[5]
            })
        
        return approvals_list
    
    def record_document(self,
                       filename: str,
                       category: str = None,
                       pages_count: int = 0,
                       chunks_count: int = 0,
                       file_size: int = 0,
                       user_session: str = None) -> str:
        """Record uploaded document"""
        
        doc_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (
                id, filename, category, pages_count, chunks_count, 
                file_size, user_session, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            filename,
            category,
            pages_count,
            chunks_count,
            file_size,
            user_session or str(uuid.uuid4()),
            'completed'
        ))
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    def get_documents(self, limit: int = 50) -> List[Dict]:
        """Get recent uploaded documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, category, pages_count, chunks_count, 
                   file_size, upload_timestamp, status
            FROM documents 
            ORDER BY upload_timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        documents_list = []
        for row in results:
            documents_list.append({
                'id': row[0],
                'filename': row[1],
                'category': row[2],
                'pages_count': row[3],
                'chunks_count': row[4],
                'file_size': row[5],
                'upload_timestamp': row[6],
                'status': row[7]
            })
        
        return documents_list
    
    def get_all_documents(self) -> List[Dict]:
        """Get all uploaded documents in current session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, category, pages_count, chunks_count, 
                   file_size, upload_timestamp, status
            FROM documents 
            ORDER BY upload_timestamp DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        documents_list = []
        for row in results:
            documents_list.append({
                'id': row[0],
                'filename': row[1],
                'category': row[2],
                'pages_count': row[3],
                'chunks_count': row[4],
                'file_size': row[5],
                'upload_timestamp': row[6],
                'status': row[7]
            })
        
        return documents_list
    
    def clear_all_documents(self) -> int:
        """Clear all document records from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM documents')
        count = cursor.fetchone()[0]
        
        cursor.execute('DELETE FROM documents')
        conn.commit()
        conn.close()
        
        return count

# Global feedback database instance
feedback_db = FeedbackDB()