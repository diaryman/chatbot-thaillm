import pandas as pd
import sqlite3
import re
import streamlit as st
import altair as alt
from src.database import get_db_connection

def parse_user_metadata(username):
    """
    Parses 'Position (Level) - Agency' string into separate fields.
    """
    if not username or not isinstance(username, str):
        return "Unknown", "Unknown", "Unknown"
    
    # Regex for "Role (Level) - Agency" or "Role - Agency"
    match = re.match(r"^(.*?)(?:\s+\((.*?)\))?\s+-\s+(.*)$", username)
    if match:
        role = match.group(1).strip()
        level = match.group(2).strip() if match.group(2) else "General"
        agency = match.group(3).strip()
        return role, level, agency
    return username, "General", "Unknown"

def get_admin_analytics():
    """
    Fetch and process data for advanced analytics.
    """
    conn = get_db_connection()
    
    try:
        # 1. Quality Stats (Rated Responses Only)
        query_quality = """
            SELECT 
                r.model_name,
                AVG(f.score_accuracy) as Accuracy,
                AVG(f.score_completeness) as Completeness,
                AVG(f.score_detail) as Detail,
                AVG(f.score_usefulness) as Usefulness,
                AVG(f.score_satisfaction) as Satisfaction,
                COUNT(f.id) as Feedback_Count
            FROM responses r
            JOIN feedback f ON r.id = f.response_id
            GROUP BY r.model_name
        """
        df_quality = pd.read_sql_query(query_quality, conn)
        
        # 2. Efficiency Stats (All Responses)
        query_efficiency = """
            SELECT 
                model_name,
                AVG(response_time) as Avg_Time_Sec,
                AVG(cost) as Avg_Cost,
                AVG(LENGTH(answer)) as Avg_Chars,
                COUNT(id) as Total_Responses
            FROM responses
            GROUP BY model_name
        """
        df_efficiency = pd.read_sql_query(query_efficiency, conn)
        
        # Merge
        if not df_efficiency.empty:
            df_models = pd.merge(df_efficiency, df_quality, on='model_name', how='left')
            cols_to_fill = ['Accuracy', 'Completeness', 'Detail', 'Usefulness', 'Satisfaction', 'Feedback_Count']
            for col in cols_to_fill:
                 if col in df_models.columns:
                     df_models[col] = df_models[col].fillna(0)
        else:
            df_models = pd.DataFrame()
        
        # 3. Monthly Usage
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
        
        # 4. Full Feedback Log for Detail Analysis
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
            LIMIT 2000
        """
        df_log = pd.read_sql_query(query_full_log, conn)
        
        # --- Post-Processing: Parse User Demographics ---
        if not df_log.empty:
            df_log[['User_Role', 'User_Level', 'User_Agency']] = df_log['username'].apply(
                lambda x: pd.Series(parse_user_metadata(x))
            )
        else:
             df_log['User_Role'] = []
             df_log['User_Level'] = []
             df_log['User_Agency'] = []

        return {
            'models': df_models,
            'usage': df_usage,
            'full_log': df_log
        }
    finally:
        conn.close()

def render_admin_dashboard():
    st.title("📊 Smart Court AI - Executive Dashboard")
    
    data = get_admin_analytics()
    df_models = data['models']
    df_log = data['full_log']
    
    if df_models.empty:
        st.info("⚠️ ยังไม่มีข้อมูลเพียงพอสำหรับการแสดงผล (No Data Available)")
        return

    # --- Top KPIs Row ---
    total_responses = df_models['Total_Responses'].sum()
    total_cost = (df_models['Avg_Cost'] * df_models['Total_Responses']).sum()
    total_feedback = df_models['Feedback_Count'].sum() if 'Feedback_Count' in df_models.columns else 0
    unique_users = df_log['username'].nunique() if not df_log.empty else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💬 Total Responses", f"{total_responses:,}")
    k2.metric("👥 Active Users", f"{unique_users:,}")
    k3.metric("⭐ Feedbacks", f"{total_feedback:,}")
    k4.metric("💰 Total Cost", f"{total_cost:,.2f} ฿")
    
    st.markdown("---")

    # ================= TABS STRUCTURE =================
    tabs = st.tabs([
        "🏆 ภาพรวม & จัดอันดับ (Overview)", 
        "👥 วิเคราะห์ผู้ใช้งาน (Demographics)", 
        "🧠 วิเคราะห์เชิงลึก (Deep Analytics)",
        "📋 ข้อมูลทั้งหมด (Full Data Logs)"
    ])

    # --- TAB 1: OVERVIEW & LEADERBOARD ---
    with tabs[0]:
        st.subheader("🏆 Model Leaderboard (จัดอันดับตามความพึงพอใจ)")
        
        if 'Satisfaction' in df_models.columns:
            # Sort and Format
            df_leaderboard = df_models.sort_values(by='Satisfaction', ascending=False).reset_index(drop=True)
            
            # Custom Highlight
            st.dataframe(
                df_leaderboard[['model_name', 'Satisfaction', 'Accuracy', 'Completeness', 'Avg_Time_Sec', 'Avg_Cost']].style.format({
                    'Satisfaction': '{:.2f} ⭐',
                    'Accuracy': '{:.2f}',
                    'Completeness': '{:.2f}',
                    'Avg_Time_Sec': '{:.2f} s',
                    'Avg_Cost': '{:.4f} ฿'
                }).background_gradient(subset=['Satisfaction'], cmap='Greens'),
                use_container_width=True
            )
        
        st.markdown("####  spider/radar chart เปรียบเทียบ 5 ด้าน")
        if 'Accuracy' in df_models.columns:
            chart_data = df_models.set_index('model_name')[
                ['Accuracy', 'Completeness', 'Detail', 'Usefulness', 'Satisfaction']
            ]
            st.bar_chart(chart_data, height=350)
            st.caption("กราฟแสดงคะแนนเฉลี่ยใน 5 มิติ ของแต่ละโมเดล")

    # --- TAB 2: USER DEMOGRAPHICS ---
    with tabs[1]:
        st.subheader("👥 ใครใช้งานระบบบ้าง? (User Demographics)")
        
        if df_log.empty:
            st.warning("No user data yet.")
        else:
            c1, c2 = st.columns(2)
            
            # Pie Chart: User Role
            with c1:
                st.markdown("**1. สัดส่วนผู้ใช้งานจำแนกตามตำแหน่ง (User Roles)**")
                role_counts = df_log.groupby('User_Role')['username'].nunique()
                st.dataframe(role_counts, use_container_width=True)
            
            # Pie Chart: Agency
            with c2:
                st.markdown("**2. สัดส่วนผู้ใช้งานจำแนกตามหน่วยงาน (Agencies)**")
                agency_counts = df_log.groupby('User_Agency')['username'].nunique()
                st.dataframe(agency_counts, use_container_width=True)
            
            st.markdown("---")
            st.markdown("**3. รายชื่อผู้ใช้งานล่าสุด (Active Users)**")
            unique_users_df = df_log[['username', 'User_Role', 'User_Level', 'User_Agency']].drop_duplicates(subset=['username'])
            st.dataframe(unique_users_df, use_container_width=True)

    # --- TAB 3: DEEP ANALYTICS ---
    with tabs[2]:
        st.subheader("🧠 Deep Dive Analysis")
        st.info("💡 ส่วนนี้ช่วยวิเคราะห์ว่า 'ใครชอบโมเดลไหน' และ 'ประสิทธิภาพเชิงลึก' เป็นอย่างไร")
        
        if not df_log.empty:
            # 1. Role Preference Heatmap
            st.markdown("#### 🎭 1. Model Preference by User Role (ตำแหน่งไหนชอบโมเดลอะไร?)")
            
            pivot_role = df_log.pivot_table(
                index='User_Role', 
                columns='model_name', 
                values='score_satisfaction', 
                aggfunc='mean'
            )
            st.dataframe(pivot_role.style.background_gradient(cmap='YlOrRd', axis=1).format("{:.2f}"), use_container_width=True)
            st.caption("ตารางแสดงคะแนนความพึงพอใจเฉลี่ย (Satisfaction) แยกตามกลุ่มผู้ใช้")
            
            # 2. Efficiency Analysis
            st.markdown("#### ⚡ 2. Efficiency vs Quality (เร็ว vs ดี)")
            eff_chart_data = df_models[['model_name', 'Avg_Time_Sec', 'Satisfaction', 'Avg_Chars']]
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**ความเร็วในการตอบ (วินาที)**")
                st.bar_chart(eff_chart_data.set_index('model_name')['Avg_Time_Sec'], color="#FFA500")
            with c2:
                st.markdown("**ความยาวคำตอบ (ตัวอักษร)**")
                st.bar_chart(eff_chart_data.set_index('model_name')['Avg_Chars'], color="#800080")
                
            # 3. Recommendations
            best_model_score = df_models.loc[df_models['Satisfaction'].idxmax()]
            fastest_model = df_models.loc[df_models['Avg_Time_Sec'].idxmin()]
            
            st.success(f"""
            **🤖 บทสรุปและคำแนะนำ (Analysis Summary):**
            - **โมเดลคุณภาพสูงสุด:** **{best_model_score['model_name']}** (Score: {best_model_score['Satisfaction']:.2f}) เป็นโมเดลที่ผู้ใช้พึงพอใจมากที่สุด
            - **โมเดลที่เร็วที่สุด:** **{fastest_model['model_name']}** (Time: {fastest_model['Avg_Time_Sec']:.2f}s) เหมาะสำหรับงานที่ต้องการความรวดเร็ว
            - **คำแนะนำ:** หากต้องการคำตอบที่แม่นยำให้เลือกใช้ **{best_model_score['model_name']}** แต่หากต้องการความเร็วให้พิจารณา **{fastest_model['model_name']}**
            """)

    # --- TAB 4: FULL DATA LOGS ---
    with tabs[3]:
        st.subheader("📋 Full Activity Logs & Export")
        
        if not df_log.empty:
            # CSV Export with parsed columns
            csv_data = df_log.drop(columns=['global_comment']).to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Full Report (CSV)",
                data=csv_data,
                file_name="smart_court_ai_full_report.csv",
                mime="text/csv",
                key="full_log_dl",
                type="primary"
            )
            
            st.markdown("##### Preview Data:")
            display_cols = ['timestamp', 'User_Role', 'User_Agency', 'question', 'model_name', 'score_satisfaction']
            st.dataframe(df_log[display_cols], use_container_width=True)
            
            with st.expander("🔎 ดูรายละเอียดรายข้อ (Expand details)"):
                for idx, row in df_log.iterrows():
                    st.markdown(f"**{row['timestamp']}** | {row['User_Role']} @ {row['User_Agency']}")
                    st.text(f"Q: {row['question']}")
                    st.caption(f"Model: {row['model_name']} | Score: {row['score_satisfaction']}/5")
                    st.divider()
        else:
            st.write("No data available.")
