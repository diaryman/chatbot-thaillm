# src/database.py
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import streamlit as st

DB_PATH = "data/court_ai.db"

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
            knowledge_base TEXT
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
    
    # Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
        )
    """)
    
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
    
    conn.commit()
    conn.close()

@st.cache_resource
def ensure_db_initialized():
    """Ensure database is initialized (cached)."""
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
    
    Args:
        username: User's name
        question: User's question
        responses_data: List of dicts with keys: model, answer, cost, time
        knowledge_base: Knowledge base used
    
    Returns:
        conversation_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert conversation
        cursor.execute("""
            INSERT INTO conversations (username, question, knowledge_base)
            VALUES (?, ?, ?)
        """, (username, question, knowledge_base))
        
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

def load_history(username: str, limit: int = 10) -> List[Dict]:
    """
    Load conversation history for a user.
    
    Args:
        username: User's name
        limit: Maximum number of conversations to load
    
    Returns:
        List of conversations with responses
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get conversations
        cursor.execute("""
            SELECT id, timestamp, question, knowledge_base
            FROM conversations
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (username, limit))
        
        conversations = []
        for conv_row in cursor.fetchall():
            conv_id = conv_row['id']
            
            # Get all responses for this conversation
            cursor.execute("""
                SELECT model_name, answer, cost, response_time
                FROM responses
                WHERE conversation_id = ?
                ORDER BY id
            """, (conv_id,))
            
            responses = [dict(row) for row in cursor.fetchall()]
            
            conversations.append({
                'id': conv_id,
                'timestamp': conv_row['timestamp'],
                'question': conv_row['question'],
                'knowledge_base': conv_row['knowledge_base'],
                'responses': responses
            })
        
        return conversations
        
    finally:
        conn.close()

def save_feedback(response_id: int, feedback_type: str):
    """
    Save user feedback for a response.
    
    Args:
        response_id: Response ID
        feedback_type: 'thumbs_up' or 'thumbs_down'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if feedback already exists
        cursor.execute("""
            SELECT id FROM feedback
            WHERE response_id = ?
        """, (response_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing feedback
            cursor.execute("""
                UPDATE feedback
                SET feedback_type = ?, created_at = CURRENT_TIMESTAMP
                WHERE response_id = ?
            """, (feedback_type, response_id))
        else:
            # Insert new feedback
            cursor.execute("""
                INSERT INTO feedback (response_id, feedback_type)
                VALUES (?, ?)
            """, (response_id, feedback_type))
        
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
