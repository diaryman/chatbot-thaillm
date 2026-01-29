import streamlit as st
import concurrent.futures
import pandas as pd
import time
import threading

from src.config import MODELS, KNOWLEDGE_BASES
from src.utils import check_secrets
from src.ui import load_custom_css, render_header, render_user_message, render_result_card, render_welcome_screen, render_copy_button
from src.services import retrieve_context, call_single_model, generate_related_questions
from src.database import ensure_db_initialized, save_conversation, load_history, save_feedback, get_response_id, get_stats
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# 1. Setup Page
st.set_page_config(page_title="Smart Court AI", page_icon="⚖️", layout="wide")

# 2. Check Secrets & DB
check_secrets()
ensure_db_initialized()

# 3. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Check Query Params for Auto-Login (Persistence)
query_params = st.query_params
restored_user = query_params.get("user", None)

if "username_confirmed" not in st.session_state:
    # If user exists in URL, restore session
    if restored_user:
        st.session_state.username = restored_user
        st.session_state.username_confirmed = True
        st.session_state.last_activity = time.time()
    else:
        st.session_state.username_confirmed = False

if "username" not in st.session_state:
    st.session_state.username = ""
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

# 3.5 Check Session Timeout (15 Minutes)
SESSION_TIMEOUT = 15 * 60  # 15 minutes in seconds

if st.session_state.username_confirmed:
    current_time = time.time()
    elapsed = current_time - st.session_state.last_activity
    
    if elapsed > SESSION_TIMEOUT:
        # Session Expired
        st.session_state.username_confirmed = False
        st.session_state.username = ""
        st.session_state.messages = []
        if "user" in st.query_params:
            del st.query_params["user"]
        st.warning("⏳ หมดเวลาการใช้งาน (Session Timeout) เนื่องจากไม่มีการใช้งานเกิน 15 นาที")
        st.stop()
    else:
        st.session_state.last_activity = current_time
        if st.session_state.username:
             st.query_params["user"] = st.session_state.username

# 4. Load Global CSS
if not st.session_state.username_confirmed:
    load_custom_css("☀️ Official Light")

# ==========================================
# 🔐 LOGIN SCREEN
# ==========================================
if not st.session_state.username_confirmed:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align: center; font-size: 80px;'>⚖️</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Smart Court AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px;'>ระบบผู้ช่วยอัจฉริยะศาลปกครอง <b>(4 ThaiLLM Models)</b></p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("##### 👤 กรุณาระบุชื่อผู้ใช้งาน (User Identification)")
            name_input = st.text_input("ชื่อของคุณ", placeholder="เช่น Officer A, สมชาย, ...", label_visibility="collapsed")
            
            if st.button("🚀 เข้าสู่ระบบ (Start)", type="primary", use_container_width=True):
                if name_input.strip():
                    st.session_state.username = name_input.strip()
                    st.session_state.username_confirmed = True
                    st.session_state.last_activity = time.time()
                    st.query_params["user"] = name_input.strip()
                    st.rerun()
                else:
                    st.warning("⚠️ กรุณากรอกชื่อก่อนเริ่มใช้งาน")
    st.stop()

# ==========================================
# 🏗️ SIDEBAR (Logged In)
# ==========================================
else:
    with st.sidebar:
        st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><div class="court-icon">⚖️</div></div>""", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Smart Court AI</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.expander("⚙️ ตั้งค่า (Settings)", expanded=True):
            theme_choice = st.radio("Theme Mode", ["🌙 Modern Dark", "☀️ Official Light"], index=1, label_visibility="collapsed")
            load_custom_css(theme_choice)
            
            st.text_input("ชื่อผู้ใช้งาน (User)", value=st.session_state.username, disabled=True)
            username = st.session_state.username
            
            temp_val = st.slider("ความสร้างสรรค์ (Temperature)", 0.0, 1.0, 0.3)
    
        st.markdown("---")
    
        # Knowledge Base Selection
        st.markdown("##### 📚 คลังข้อมูล (Knowledge Base)")
        kb_name = st.selectbox("เลือกแหล่งข้อมูล", list(KNOWLEDGE_BASES.keys()), index=0, key="kb_select")
        kb_id = KNOWLEDGE_BASES[kb_name]
        
        st.info(f"ระบบจะใช้ **{kb_name}** ในการค้นหาคำตอบสำหรับทั้ง 4 โมเดล")

        st.markdown("---")
        
        # Log Viewer
        if "system_logs" not in st.session_state:
            st.session_state.system_logs = []

        with st.expander("🛠️ System Logs", expanded=False):
            if st.button("Clear Logs", type="secondary", use_container_width=True):
                st.session_state.system_logs = []
                st.rerun()
            
            if not st.session_state.system_logs:
                st.caption("No logs yet.")
            else:
                for log in reversed(st.session_state.system_logs):
                    st.text(log)
                    st.divider()

        # Model Selection
        st.markdown("##### 🤖 เลือกโมเดลที่ต้องการ (Select Models)")
        all_model_names = list(MODELS.keys())
        default_models = all_model_names[:4]
        
        selected_models = st.multiselect(
            "เลือกโมเดลเพื่อเปรียบเทียบ",
            options=all_model_names,
            default=default_models,
            label_visibility="collapsed"
        )
        
        if not selected_models:
            st.warning("⚠️ กรุณาเลือกอย่างน้อย 1 โมเดล")
            st.stop()

        st.markdown("---")
        
        col_clr, col_save = st.columns(2)
        if col_clr.button("🗑️ Reset", use_container_width=True):
            st.session_state.messages = []
            if 'auto_run_prompt' in st.session_state: del st.session_state['auto_run_prompt']
            st.rerun()
            
        if st.session_state.get("messages"):
            chat_str = "\n".join([f"{m['role']}: {m['content']}" if m['role']=='user' else "AI Reponse" for m in st.session_state.messages])
            col_save.download_button("📥 Save", chat_str, "log.txt", use_container_width=True)
    
    # ==========================================
    # 🖥️ MAIN CONTENT (Logged In)
    # ==========================================
    
    # Feedback Callback Logic
    def handle_feedback(response_id, score, model_name):
        if response_id:
            try:
                # Store score as string "1" to "5"
                save_feedback(response_id, str(score))
                st.toast(f"✅ บันทึกคะแนนเรียบร้อย ({score} ดาว)", icon="⭐")
            except Exception as e:
                st.error(f"Error saving feedback: {e}")

    render_header()
    tab_chat, tab_hist = st.tabs([f"💬 สนทนา {len(selected_models)} โมเดล", "📜 ประวัติ (History)"])
    
    def get_grid_cols(n_models):
        if n_models == 1: return st.columns(1)
        elif n_models == 2: return st.columns(2)
        else: return st.columns(2) + st.columns(2)

    # --- Tab 1: Chat ---
    with tab_chat:
        chat_container = st.container()
        
        # Ensure Welcome Screen Placeholder is managed
        welcome_ph = st.empty()
        
        prompt = None
        if 'auto_run_prompt' in st.session_state:
            prompt = st.session_state['auto_run_prompt']
            del st.session_state['auto_run_prompt']
        
        # Show Welcome Screen ONLY if history is empty and no active prompt
        if len(st.session_state.messages) == 0 and not prompt:
            with welcome_ph:
                render_welcome_screen()
                s_cols = st.columns(3)
                questions = [
                    "ขั้นตอนการยื่นฟ้องคดีปกครองทำอย่างไร?",
                    "ศาลปกครองมีอำนาจพิจารณาคดีประเภทใดบ้าง?",
                    "การขอทุเลาการบังคับตามคำสั่งทางปกครองคืออะไร?"
                ]
                for i, q in enumerate(questions):
                    with s_cols[i]:
                        if st.button(q, use_container_width=True):
                            st.session_state['auto_run_prompt'] = q
                            st.rerun()
        else:
            welcome_ph.empty() # Fix Phantom Text
        
        # Render Chat History
        for msg_idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                render_user_message(msg["content"])
            else:
                results = msg.get("results", {})
                models_to_show = [m for m in selected_models if m in results]
                
                if not models_to_show:
                    st.warning("⚠️ ประวัตินี้ไม่มีโมเดลที่ท่านเลือกในปัจจุบัน")
                    continue

                cols = get_grid_cols(len(models_to_show))
                
                for i, m_key in enumerate(models_to_show):
                    res = results[m_key]
                    with cols[i]:
                        render_result_card(res, kb_name)
                        
                        # 5-Star Feedback
                        score = st.feedback("stars", key=f"star_{msg_idx}_{m_key}")
                        if score is not None:
                            # score is 0-4, map to 1-5? Or keep 0-4? usually user expects 1-5.
                            # Standard UI usually maps indices. Let's send real score + 1.
                            # But wait, st.feedback returns 0-based index?
                            # Documentation: "The index of the selected option, starting from 0."
                            # So 0 = 1 star, 4 = 5 stars.
                            handle_feedback(res.get('db_id'), score + 1, m_key)
                            
                        render_copy_button(res['answer'], f"hist_{i}_{len(str(results))}")
                
                # Render Suggested Questions (if any) for the latset message
                suggestions = msg.get("suggestions", [])
                if suggestions:
                    st.write("---")
                    st.caption("💡 คำถามที่เกี่ยวข้อง (Suggested Questions):")
                    s_cols = st.columns(len(suggestions))
                    for si, s_q in enumerate(suggestions):
                        with s_cols[si]:
                            if st.button(s_q, key=f"sugg_{msg_idx}_{si}", use_container_width=True):
                                st.session_state['auto_run_prompt'] = s_q
                                st.rerun()

        # User Input
        if prompt := (prompt or st.chat_input("พิมพ์คำถามของคุณที่นี่...")):
            # Clear welcome screen instantly (optimistic)
            welcome_ph.empty()
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            render_user_message(prompt)
            
            # Prepare Dynamic Layout
            n_models = len(selected_models)
            cols = get_grid_cols(n_models)
            placeholders = []
            
            for col in cols:
                placeholders.append(col.empty())
            
            # Threading Helper
            main_ctx = get_script_run_ctx()
            def task_with_ctx(func, *args, **kwargs):
                add_script_run_ctx(threading.current_thread(), main_ctx)
                return func(*args, **kwargs)

            # 1. Retrieve Context
            with st.spinner(f"🔍 กำลังค้นหาข้อมูลจาก {kb_name}..."):
                ctx_text, citation_details = retrieve_context(prompt, kb_id)
                
            # 2. Call Models
            with st.spinner("⚡ AI กำลังประมวลผลและสร้างคำตอบ (AI is thinking)..."):
                with concurrent.futures.ThreadPoolExecutor(max_workers=n_models) as executor:
                    futures = {}
                    for i, m_key in enumerate(selected_models):
                        future = executor.submit(task_with_ctx, call_single_model, m_key, prompt, ctx_text, citation_details, temp_val)
                        futures[future] = m_key, i 
                        
                    results = {}
                    for future in concurrent.futures.as_completed(futures):
                        res = future.result()
                        m_key, idx = futures[future]
                        results[res['model']] = res
                        
                        placeholders[idx].empty()
                        with cols[idx]:
                            render_result_card(res, kb_name)
                            # No feedback in live stream for cleaner UI
                            render_copy_button(res['answer'], f"live_{idx}")
            
            # 3. Save to DB
            responses_list = [results[m] for m in selected_models if m in results]
            
            if username:
                conv_id = save_conversation(username, prompt, responses_list, kb_name)
                # Attach IDs
                for res in results.values():
                    res['db_id'] = get_response_id(conv_id, res['model'])

            # 4. Generate Suggestions (Post-Response)
            suggestions = []
            with st.spinner("💡 กำลังคิดคำถามแนะนำ (Thinking next questions)..."):
                # Use the first selected model (or 'Typhoon') for suggestions
                model_for_sugg = selected_models[0] if selected_models else "Typhoon"
                suggestions = generate_related_questions(prompt, ctx_text, model_name=model_for_sugg)
                
            if not suggestions:
                st.toast("⚠️ ไม่สามารถสร้างคำถามแนะนำได้ (API Error or Empty)", icon="⚠️")

            # 5. Save to State
            st.session_state.messages.append({
                "role": "assistant",
                "results": results,
                "kb_name": kb_name,
                "conversation_id": conv_id if username else None,
                "suggestions": suggestions
            })
            
            # 6. Rerun to show everything properly (Stars + Suggestions)
            st.rerun()

    # --- Tab 2: History ---
    with tab_hist:
        st.subheader(f"📜 ประวัติการใช้งาน: {username}")
        if st.button("🔄 รีเฟรชข้อมูล"): st.rerun()
        
        history = load_history(username, limit=20)
        stats = get_stats(username)
        
        if history:
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("ประวัติการสนทนา", f"{stats['total_conversations']} ครั้ง")
            col_s2.metric("ค่าใช้จ่ายรวม", f"{stats['total_cost']:.2f} THB")
            
            search_q = st.text_input("🔍 ค้นหาประวัติ", "")
            
            for conv in history:
                if search_q and search_q not in conv['question']: continue
                
                with st.expander(f"🕒 {conv['timestamp']} | ❓ {conv['question'][:50]}..."):
                    st.write(f"**Question:** {conv['question']}")
                    st.caption(f"Knowledge Base: {conv['knowledge_base']}")
                    h_cols = st.columns(2) + st.columns(2)
                    for i, resp in enumerate(conv['responses']):
                        if i < 4:
                            with h_cols[i]:
                                st.markdown(f"**{resp['model_name']}**")
                                st.info(resp['answer'])
                                st.caption(f"Cost: {resp['cost']} THB")
        else:
            st.info("ยังไม่มีประวัติการใช้งาน")
