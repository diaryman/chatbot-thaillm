# src/database.py
import sqlite3
import os
from datetime import datetime
import pytz
from typing import List, Dict, Optional, Tuple
import streamlit as st

DB_PATH = "data/court_ai.db"

def get_thai_time():
    """Get current time in Asia/Bangkok timezone."""
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(bangkok_tz)

def get_db_connection():
    """Get database connection with proper configuration."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT NOT NULL,
            question TEXT NOT NULL,
            knowledge_base TEXT,
            user_comment TEXT
        )
    """)
    
    # Responses table (for 4 models)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            answer TEXT NOT NULL,
            cost REAL DEFAULT 0.0,
            response_time REAL DEFAULT 0.0,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """)
    
    # Feedback table (Updated with 5 dimensions + comment)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER NOT NULL,
            feedback_type TEXT, -- Legacy, kept for compatibility
            score_accuracy INTEGER,
            score_completeness INTEGER,
            score_detail INTEGER,
            score_usefulness INTEGER,
            score_satisfaction INTEGER,
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
        )
    """)
    
    # Migration: Add columns if they don't exist
    # 1. Feedback table columns
    columns_to_add = [
        ("score_accuracy", "INTEGER"),
        ("score_completeness", "INTEGER"),
        ("score_detail", "INTEGER"),
        ("score_usefulness", "INTEGER"),
        ("score_satisfaction", "INTEGER"),
        ("comment", "TEXT")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE feedback ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # 2. Conversations table columns
    try:
        cursor.execute("ALTER TABLE conversations ADD COLUMN user_comment TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_username 
        ON conversations(username)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_responses_conversation 
        ON responses(conversation_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feedback_response 
        ON feedback(response_id)
    """)
    
    # Explicit Migration Check using PRAGMA
    # 1. Check conversations table
    cursor.execute("PRAGMA table_info(conversations)")
    cov_cols = [r['name'] for r in cursor.fetchall()]
    
    if 'user_comment' not in cov_cols:
        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN user_comment TEXT")
            print("Migration: Added user_comment to conversations")
        except Exception as e:
            print(f"Error adding user_comment column: {e}")
            # Do not suppress critical errors

    # 2. Check feedback table columns
    cursor.execute("PRAGMA table_info(feedback)")
    feed_cols = [r['name'] for r in cursor.fetchall()]
    
    needed_feedback_cols = [
        ("score_accuracy", "INTEGER"),
        ("score_completeness", "INTEGER"),
        ("score_detail", "INTEGER"),
        ("score_usefulness", "INTEGER"),
        ("score_satisfaction", "INTEGER"),
        ("comment", "TEXT")
    ]
    
    for col_name, col_type in needed_feedback_cols:
        if col_name not in feed_cols:
            try:
                cursor.execute(f"ALTER TABLE feedback ADD COLUMN {col_name} {col_type}")
                print(f"Migration: Added {col_name} to feedback")
            except Exception as e:
                print(f"Error adding {col_name} to feedback: {e}")

    conn.commit()
    conn.close()

# Removed @st.cache_resource to ensure migration check runs on reload
def ensure_db_initialized():
    """Ensure database is initialized."""
    init_db()
    return True

def save_conversation(
    username: str, 
    question: str, 
    responses_data: List[Dict],
    knowledge_base: str = ""
) -> int:
    """
    Save a conversation with all 4 model responses.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get Thai Time
    current_time = get_thai_time()
    
    try:
        # Insert conversation with explicit timestamp
        cursor.execute("""
            INSERT INTO conversations (username, question, knowledge_base, timestamp)
            VALUES (?, ?, ?, ?)
        """, (username, question, knowledge_base, current_time))
        
        conversation_id = cursor.lastrowid
        
        # Insert all responses
        for resp in responses_data:
            cursor.execute("""
                INSERT INTO responses 
                (conversation_id, model_name, answer, cost, response_time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                conversation_id,
                resp.get('model', ''),
                resp.get('answer', ''),
                resp.get('cost', 0.0),
                resp.get('time', 0.0)
            ))
        
        conn.commit()
        return conversation_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_conversation_comment(conversation_id: int, comment: str):
    """
    Save user comment/correct answer for the conversation (question).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE conversations 
            SET user_comment = ? 
            WHERE id = ?
        """, (comment, conversation_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def load_history(username: str, limit: int = 10) -> List[Dict]:
    """
    Load conversation history for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get conversations
        cursor.execute("""
            SELECT id, timestamp, question, knowledge_base, user_comment
            FROM conversations
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (username, limit))
        
        conversations = []
        for conv_row in cursor.fetchall():
            conv_id = conv_row['id']
            
            # Get all responses and their feedback for this conversation
            cursor.execute("""
                SELECT r.id, r.model_name, r.answer, r.cost, r.response_time,
                       f.score_accuracy, f.score_completeness, f.score_detail, 
                       f.score_usefulness, f.score_satisfaction, f.comment as fb_comment
                FROM responses r
                LEFT JOIN feedback f ON r.id = f.response_id
                WHERE r.conversation_id = ?
                ORDER BY r.id
            """, (conv_id,))
            
            responses = [dict(row) for row in cursor.fetchall()]
            
            conversations.append({
                'id': conv_id,
                'timestamp': conv_row['timestamp'],
                'question': conv_row['question'],
                'knowledge_base': conv_row['knowledge_base'],
                'comment': conv_row['user_comment'] or "", 
                'responses': responses
            })
        
        return conversations
        
    finally:
        conn.close()

def save_feedback(
    response_id: int, 
    accuracy: int = 0,
    completeness: int = 0,
    detail: int = 0,
    usefulness: int = 0,
    satisfaction: int = 0,
    comment: str = ""
):
    """
    Save or update user feedback for a response.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_time = get_thai_time()
    
    try:
        # Check if feedback already exists for this response
        cursor.execute("SELECT id FROM feedback WHERE response_id = ?", (response_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute("""
                UPDATE feedback
                SET score_accuracy = ?,
                    score_completeness = ?,
                    score_detail = ?,
                    score_usefulness = ?,
                    score_satisfaction = ?,
                    comment = ?,
                    created_at = ?
                WHERE response_id = ?
            """, (accuracy, completeness, detail, usefulness, satisfaction, comment, current_time, response_id))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO feedback (
                    response_id, 
                    score_accuracy, score_completeness, score_detail, score_usefulness, score_satisfaction,
                    comment, feedback_type, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'detailed', ?)
            """, (response_id, accuracy, completeness, detail, usefulness, satisfaction, comment, current_time))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_response_id(conversation_id: int, model_name: str) -> Optional[int]:
    """
    Get response ID for a specific model in a conversation.
    
    Args:
        conversation_id: Conversation ID
        model_name: Model name
    
    Returns:
        Response ID or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id FROM responses
            WHERE conversation_id = ? AND model_name = ?
        """, (conversation_id, model_name))
        
        row = cursor.fetchone()
        return row['id'] if row else None
        
    finally:
        conn.close()

def get_stats(username: Optional[str] = None) -> Dict:
    """
    Get usage statistics.
    
    Args:
        username: Optional username filter
    
    Returns:
        Dict with statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        where_clause = "WHERE username = ?" if username else ""
        params = (username,) if username else ()
        
        # Total conversations
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM conversations
            {where_clause}
        """, params)
        total_conversations = cursor.fetchone()['count']
        
        # Total cost
        cursor.execute(f"""
            SELECT SUM(r.cost) as total_cost
            FROM responses r
            JOIN conversations c ON r.conversation_id = c.id
            {where_clause}
        """, params)
        total_cost = cursor.fetchone()['total_cost'] or 0.0
        
        # Average response time per model
        cursor.execute(f"""
            SELECT r.model_name, AVG(r.response_time) as avg_time
            FROM responses r
            JOIN conversations c ON r.conversation_id = c.id
            {where_clause}
            GROUP BY r.model_name
        """, params)
        avg_times = {row['model_name']: row['avg_time'] for row in cursor.fetchall()}
        
        return {
            'total_conversations': total_conversations,
            'total_cost': total_cost,
            'avg_response_times': avg_times
        }
        
    finally:
        conn.close()
