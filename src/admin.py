import pandas as pd
import sqlite3
import streamlit as st
from src.database import get_db_connection

def get_admin_analytics():
    """
    Fetch aggregated feedback and usage data for the admin dashboard.
    """
    conn = get_db_connection()
    
    try:
        # 1. Model Performance (Average Ratings)
        query_ratings = """
            SELECT 
                r.model_name,
                AVG(f.score_accuracy) as avg_accuracy,
                AVG(f.score_completeness) as avg_completeness,
                AVG(f.score_detail) as avg_detail,
                AVG(f.score_usefulness) as avg_usefulness,
                AVG(f.score_satisfaction) as avg_satisfaction,
                COUNT(f.id) as feedback_count
            FROM responses r
            JOIN feedback f ON r.id = f.response_id
            GROUP BY r.model_name
        """
        df_ratings = pd.read_sql_query(query_ratings, conn)
        
        # 2. Monthly Usage & Cost
        query_usage = """
            SELECT 
                strftime('%Y-%m', timestamp) as month,
                COUNT(id) as total_conversations,
                SUM(cost) as total_cost
            FROM conversations
            GROUP BY month
            ORDER BY month DESC
        """
        # Note: cost is in responses table, matching by conversation_id
        query_usage_total = """
            SELECT 
                strftime('%Y-%m', c.timestamp) as month,
                COUNT(DISTINCT c.id) as conversations,
                SUM(r.cost) as cost
            FROM conversations c
            JOIN responses r ON c.id = r.conversation_id
            GROUP BY month
            ORDER BY month DESC
        """
        df_usage = pd.read_sql_query(query_usage_total, conn)
        
        # 3. Recent Feedback with Comments
        query_comments = """
            SELECT 
                c.username,
                c.question,
                r.model_name,
                f.score_satisfaction,
                f.comment as feedback_comment,
                c.user_comment as suggested_answer,
                c.timestamp
            FROM responses r
            JOIN feedback f ON r.id = f.response_id
            JOIN conversations c ON r.conversation_id = c.id
            WHERE f.comment != '' OR c.user_comment IS NOT NULL
            ORDER BY c.timestamp DESC
            LIMIT 50
        """
        df_comments = pd.read_sql_query(query_comments, conn)
        
        return {
            'ratings': df_ratings,
            'usage': df_usage,
            'comments': df_comments
        }
    finally:
        conn.close()

def render_admin_dashboard():
    """
    Renders the admin dashboard with charts and tables.
    """
    st.title("📊 Admin Insights Dashboard")
    
    data = get_admin_analytics()
    
    if data['ratings'].empty:
        st.info("ยังไม่มีข้อมูลการประเมินผล (No feedback data yet)")
        return

    # --- Top KPIs ---
    total_convs = data['usage']['conversations'].sum()
    total_cost = data['usage']['cost'].sum()
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Interactions", f"{total_convs} ✨")
    k2.metric("Total API Cost", f"{total_cost:.2f} THB")
    k3.metric("Models Monitored", len(data['ratings']))

    # --- Charts Section ---
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("⭐ Average Satisfaction by Model")
        st.bar_chart(data['ratings'].set_index('model_name')['avg_satisfaction'])
        
    with c2:
        st.subheader("💰 Monthly Cost Trend")
        if not data['usage'].empty:
            st.line_chart(data['usage'].set_index('month')['cost'])

    # --- Detailed Ratings Table ---
    st.markdown("---")
    st.subheader("📈 Multi-Dimensional Rating Breakdown")
    st.dataframe(
        data['ratings'].rename(columns={
            'avg_accuracy': 'Accuracy',
            'avg_completeness': 'Completeness',
            'avg_detail': 'Detail',
            'avg_usefulness': 'Usefulness',
            'avg_satisfaction': 'Overall',
            'feedback_count': 'Count'
        }).style.background_gradient(cmap='Blues'),
        use_container_width=True
    )

    # --- Feedback & Suggested Answers ---
    st.markdown("---")
    st.subheader("💬 User Suggestions & Corrected Answers")
    if not data['comments'].empty:
        for idx, row in data['comments'].iterrows():
            with st.expander(f"👤 {row['username']} | {row['timestamp']}"):
                st.markdown(f"**Question:** {row['question']}")
                st.markdown(f"**Model:** {row['model_name']} (⭐ {row['score_satisfaction']})")
                if row['feedback_comment']:
                    st.info(f"**User Feedback:** {row['feedback_comment']}")
                if row['suggested_answer']:
                    st.success(f"**Suggested Correct Answer:** {row['suggested_answer']}")
    else:
        st.write("No specific comments yet.")
