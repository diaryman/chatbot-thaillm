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
        
        # 3. Full Feedback Log (All ratings, even without comments)
        query_full_log = """
            SELECT 
                c.id as conversation_id,
                c.username,
                c.question,
                r.model_name,
                f.score_accuracy,
                f.score_completeness,
                f.score_detail,
                f.score_usefulness,
                f.score_satisfaction,
                f.comment as feedback_comment,
                c.user_comment as global_comment,
                c.timestamp
            FROM responses r
            JOIN feedback f ON r.id = f.response_id
            JOIN conversations c ON r.conversation_id = c.id
            ORDER BY c.timestamp DESC
            LIMIT 100
        """
        df_log = pd.read_sql_query(query_full_log, conn)
        
        return {
            'ratings': df_ratings,
            'usage': df_usage,
            'full_log': df_log
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
    total_convs = data['usage']['conversations'].sum() if not data['usage'].empty else 0
    total_cost = data['usage']['cost'].sum() if not data['usage'].empty else 0.0
    
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

    # --- Full Feedback Log ---
    st.markdown("---")
    st.subheader("📋 Full User Activity Log (Who gave what stars?)")
    
    if not data['full_log'].empty:
        # Display as a dataframe for easy sorting/filtering
        display_df = data['full_log'][['timestamp', 'username', 'question', 'model_name', 'score_satisfaction', 'feedback_comment']]
        st.dataframe(display_df, use_container_width=True)
        
        # Detailed Expanders
        with st.expander("🔎 View Detailed Feedback Logs (Click to expand)"):
            for idx, row in data['full_log'].iterrows():
                # Create a label with User + Time + Rating
                label = f"{row['timestamp']} | 👤 {row['username']} | ⭐ {row['score_satisfaction']}/5"
                st.markdown(f"**{label}**")
                
                # Content
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.caption("Ratings Breakdown:")
                    st.write(f"- Accuracy: {row['score_accuracy']}")
                    st.write(f"- Completeness: {row['score_completeness']}")
                    st.write(f"- Detail: {row['score_detail']}")
                    st.write(f"- Usefulness: {row['score_usefulness']}")
                with c2:
                    st.write(f"**Q:** {row['question']}")
                    st.write(f"**Model:** {row['model_name']}")
                    if row['feedback_comment']:
                        st.info(f"💬 Comment: {row['feedback_comment']}")
                    if row['global_comment']:
                        st.success(f"💡 Suggestion: {row['global_comment']}")
                st.divider()
    else:
        st.write("No activity logs yet.")
