import streamlit as st
import concurrent.futures
import pandas as pd

from src.config import MODELS, KNOWLEDGE_BASES
from src.utils import check_secrets
from src.ui import load_custom_css, render_header, render_user_message, render_result_card, render_welcome_screen, render_copy_button
from src.services import retrieve_context, call_single_model, save_to_sheet, load_history_from_sheet, save_feedback

from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# 1. Setup Page
st.set_page_config(page_title="Smart Court AI", page_icon="⚖️", layout="wide")

# 2. Check Secrets
check_secrets()

# 3. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username_confirmed" not in st.session_state:
    st.session_state.username_confirmed = False
if "username" not in st.session_state:
    st.session_state.username = ""

# 4. Load Global CSS (Default Theme)
# We load "Official Light" by default for Login Screen, or respect previous choice if saved (optional)
# For simplicity, we stick to Official Light as default if not logged in.
if not st.session_state.username_confirmed:
    load_custom_css("☀️ Official Light")

# ==========================================
# 🔐 LOGIN SCREEN
# ==========================================
if not st.session_state.username_confirmed:
    # Use empty container for centering
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align: center; font-size: 80px;'>⚖️</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Smart Court AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px;'>ระบบผู้ช่วยอัจฉริยะศาลปกครอง</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("##### 👤 กรุณาระบุชื่อผู้ใช้งาน (User Identification)")
            name_input = st.text_input("ชื่อของคุณ", placeholder="เช่น Officer A, สมชาย, ...", label_visibility="collapsed")
            
            if st.button("🚀 เข้าสู่ระบบ (Start)", type="primary", use_container_width=True):
                if name_input.strip():
                    st.session_state.username = name_input.strip()
                    st.session_state.username_confirmed = True
                    st.rerun()
                else:
                    st.warning("⚠️ กรุณากรอกชื่อก่อนเริ่มใช้งาน")
    
    st.stop()

else:
    # ==========================================
    # 🏗️ SIDEBAR (Logged In)
    # ==========================================
    with st.sidebar:
        st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><div class="court-icon">⚖️</div></div>""", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Smart Court AI</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.expander("⚙️ ตั้งค่า (Settings)", expanded=True):
            theme_choice = st.radio("Theme Mode", ["🌙 Modern Dark", "☀️ Official Light"], index=1, label_visibility="collapsed")
            load_custom_css(theme_choice) # Inject CSS dynamically based on choice
            
            # Show Username (Read-only or Disabled)
            st.text_input("ชื่อผู้ใช้งาน (User)", value=st.session_state.username, disabled=True)
            # username = st.text_input("ชื่อผู้ใช้งาน (User)", value="Officer") # OLD Code
            username = st.session_state.username # Use state value
            
            temp_val = st.slider("ความสร้างสรรค์ (Temperature)", 0.0, 1.0, 0.3)
    
        st.markdown("---")
    
        # Double Compare Config
        st.markdown("##### ⚔️ Model Comparison")
        
        # Left Side
        with st.container(border=True):
            st.caption("👈 ฝั่งซ้าย (Left Side)")
            kb_left_name = st.selectbox("คลังข้อมูล", list(KNOWLEDGE_BASES.keys()), index=0, key="kb_l")
            m_left = st.selectbox("โมเดล", list(MODELS.keys()), index=0, key="md_l")
    
        # Right Side
        with st.container(border=True):
            st.caption("👉 ฝั่งขวา (Right Side)")
            kb_right_name = st.selectbox("คลังข้อมูล ", list(KNOWLEDGE_BASES.keys()), index=0, key="kb_r")
            m_right = st.selectbox("โมเดล ", list(MODELS.keys()), index=1 if len(MODELS) > 1 else 0, key="md_r")
        
        # Get IDs
        kb_left_id = KNOWLEDGE_BASES[kb_left_name]
        kb_right_id = KNOWLEDGE_BASES[kb_right_name]
    
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
    
    # Callback for Feedback
    def handle_feedback(key, username, prompt, model, answer):
        score_idx = st.session_state[key]
        if score_idx is not None:
             score = score_idx + 1
             save_feedback(username, prompt, model, score, answer)
             st.toast(f"✅ บันทึกคะแนน {score} ดาว เรียบร้อยแล้ว! (Model: {model})", icon="⭐")


render_header()
tab_chat, tab_hist = st.tabs(["💬 สนทนา (Chat)", "📜 ประวัติ ((History)"])

# --- Tab 1: Chat ---
with tab_chat:
    chat_container = st.container()
    
    # Logic to handle prompt input (either from text input or button click)
    prompt = None
    
    # Handle Auto-Run Prompt (Regenerate)
    if 'auto_run_prompt' in st.session_state:
        prompt = st.session_state['auto_run_prompt']
        # Clear it immediately so it doesn't loop, but we need to ensure it processes
        del st.session_state['auto_run_prompt']
    
    # Show Welcome Screen if no messages and no prompt
    if len(st.session_state.messages) == 0 and not prompt:
        render_welcome_screen()
        
        # Suggested Questions
        s_cols = st.columns(3)
        questions = [
            "ขั้นตอนการยื่นฟ้องคดีปกครองทำอย่างไร?",
            "ศาลปกครองมีอำนาจพิจารณาคดีประเภทใดบ้าง?",
            "การขอทุเลาการบังคับตามคำสั่งทางปกครองคืออะไร?"
        ]
        
        for i, q in enumerate(questions):
            with s_cols[i]:
                if st.button(q, key=f"s_btn_{i}", use_container_width=True):
                    prompt = q
    
    # Display History
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🧑‍💼"): 
                    render_user_message(msg['content'])
            else:
                with st.chat_message("assistant", avatar="⚖️"):
                    # Try to get prompt from previous message
                    prompt_text = "History"
                    if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                        prompt_text = st.session_state.messages[i-1]["content"]

                    c1, c2 = st.columns(2)
                    with c1: 
                        render_result_card(msg["left"], msg["kb_l_name"])
                        # Copy Button
                        render_copy_button(msg["left"]['answer'], f"hist_l_{i}")
                        
                        # Feedback Left (History)
                        st.feedback("stars", key=f"hist_fb_l_{i}", on_change=handle_feedback, args=(f"hist_fb_l_{i}", username, prompt_text, msg["left"]['model'], msg["left"]['answer']))

                    with c2: 
                        render_result_card(msg["right"], msg["kb_r_name"])
                        # Copy Button
                        render_copy_button(msg["right"]['answer'], f"hist_r_{i}")
                        
                        # Feedback Right (History)
                        st.feedback("stars", key=f"hist_fb_r_{i}", on_change=handle_feedback, args=(f"hist_fb_r_{i}", username, prompt_text, msg["right"]['model'], msg["right"]['answer']))
    
    # Regenerate Button (Show only if history exists)
    if len(st.session_state.messages) > 0:
        st.divider()
        col_regen, _ = st.columns([1, 4])
        if col_regen.button("🔄 ถามซ้ำ (Regenerate Response)", help="กดเพื่อเริ่มการคำนวณใหม่สำหรับคำถามล่าสุด"):
             # Logic: Check if last msg is assistant
             if st.session_state.messages and st.session_state.messages[-1]['role'] == 'assistant':
                last_conv = st.session_state.messages[-2] # User msg
                if last_conv['role'] == 'user':
                    st.session_state.messages.pop() # Pop Assistant
                    st.session_state.messages.pop() # Pop Client (prevent cleanup issues)
                    
                    st.session_state['auto_run_prompt'] = last_conv['content']
                    st.rerun()

    # Chat Input (Bottom)
    input_text = st.chat_input("พิมพ์คำถามของคุณที่นี่...")
    if input_text:
        prompt = input_text

    # Process Prompt
    if prompt:
        with chat_container:
            # Render user message manually if it wasn't already in history (for auto-run, it might have been popped)
            # But wait, we popped it, so we need to re-add it/render it.
            
            # If prompt came from text_input, streamlit renders it.
            # If prompt came from button (suggested or regen), we render it manually.
            
            # Simple check: Is this prompt the last message in state?
            if not st.session_state.messages or st.session_state.messages[-1].get('content') != prompt:
                 with st.chat_message("user", avatar="🧑‍💼"): 
                    render_user_message(prompt)
                 st.session_state.messages.append({"role": "user", "content": prompt})

            # 2. Assistant Processing
            with st.chat_message("assistant", avatar="⚖️"):
                # Prepare Layout for 2 models side-by-side
                c1, c2 = st.columns(2)
                
                # We need placeholders for streaming content
                with c1: 
                    # Initial Card Structure for Left
                    ph_l = st.empty()
                    ph_l.markdown(f"⏳ **{m_left}**: กำลังประมวลผล...")

                with c2:
                    # Initial Card Structure for Right
                    ph_r = st.empty()
                    ph_r.markdown(f"⏳ **{m_right}**: กำลังประมวลผล...")

                status = st.status("🔍 กำลังค้นหาข้อมูลจากคลังข้อมูล...", expanded=True)
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Step A: Retrieve Context (Blocking)
                    status.write("📚 Searching Knowledge Repositories...")
                    
                    # Capture context
                    ctx = get_script_run_ctx()
                    
                    def task_with_ctx(func, *args, **kwargs):
                        add_script_run_ctx(ctx=ctx)
                        return func(*args, **kwargs)

                    f_ctx_l = executor.submit(task_with_ctx, retrieve_context, prompt, kb_left_id)
                    f_ctx_r = executor.submit(task_with_ctx, retrieve_context, prompt, kb_right_id)
                    
                    ctx_l, cite_l = f_ctx_l.result()
                    ctx_r, cite_r = f_ctx_r.result()
                    
                    # Step B: Call Models with Streaming (Concurrent)
                    status.write("⚡ Generating Responses...")
                    
                    f1 = executor.submit(task_with_ctx, call_single_model, m_left, prompt, ctx_l, cite_l, temp_val, ph_l)
                    f2 = executor.submit(task_with_ctx, call_single_model, m_right, prompt, ctx_r, cite_r, temp_val, ph_r)
                    
                    res_l = f1.result()
                    res_r = f2.result()
                
                status.update(label="✅ เสร็จสิ้น", state="complete", expanded=False)
                
                # Render Final Beautified Results (Replacing the streaming text)
                ph_l.empty()
                ph_r.empty()
                
                with c1: 
                    render_result_card(res_l, kb_left_name)
                    # Copy Button
                    render_copy_button(res_l['answer'], f"live_l_{len(st.session_state.messages)}")
                    
                    # Feedback Left
                    st.caption("ให้คะแนนคำตอบ:")
                    st.feedback("stars", key=f"hist_fb_l_{len(st.session_state.messages)}", on_change=handle_feedback, args=(f"hist_fb_l_{len(st.session_state.messages)}", username, prompt, res_l['model'], res_l['answer']))
                        
                with c2: 
                    render_result_card(res_r, kb_right_name)
                    # Copy Button
                    render_copy_button(res_r['answer'], f"live_r_{len(st.session_state.messages)}")
                    
                    # Feedback Right
                    st.caption("ให้คะแนนคำตอบ:")
                    st.feedback("stars", key=f"hist_fb_r_{len(st.session_state.messages)}", on_change=handle_feedback, args=(f"hist_fb_r_{len(st.session_state.messages)}", username, prompt, res_r['model'], res_r['answer']))

                # Save to State
                st.session_state.messages.append({
                    "role": "assistant", 
                    "left": res_l, 
                    "right": res_r, 
                    "kb_l_name": kb_left_name, 
                    "kb_r_name": kb_right_name
                })
                
                # Save to Sheet
                if username: 
                    save_to_sheet(username, prompt, res_l, res_r, kb_left_name, kb_right_name)

# --- Tab 2: History ---
with tab_hist:
    st.subheader(f"📜 ประวัติการใช้งาน: {username}")
    
    # Refresh Button
    if st.button("🔄 รีเฟรชข้อมูล (Refresh)"): 
        st.cache_data.clear()
        st.rerun()
        
    df = load_history_from_sheet(username)
    
    if not df.empty:
        # Search Filter
        search_query = st.text_input("🔍 ค้นหาประวัติ (Search History)", "").lower()
        
        # Reverse to show newest first
        df = df.iloc[::-1]
        
        # Metrics Summary
        total_cost = 0.0
        try:
             # Clean up cost columns (remove string format if needed, though they are usually strings in CSV)
             # We assume columns 7 and 12 are costs based on latest schema
             c_left = pd.to_numeric(df.iloc[:, 7], errors='coerce').sum()
             c_right = pd.to_numeric(df.iloc[:, 12], errors='coerce').sum()
             total_cost = c_left + c_right
        except:
            pass
            
        st.caption(f"💰 รวมค่าใช้จ่ายทั้งหมด: {total_cost:.4f} THB | 📝 จำนวนรายการ: {len(df)}")
        st.divider()

        count = 0
        for index, row in df.iterrows():
            # Data Mapping (Safe Access)
            try:
                # Based on latest schema:
                # 0:Time, 1:User, 2:Q, 3:KB_L, 4:Mod_L, 5:Ans_L, 6:FB_L, 7:Cost_L, 8:KB_R, 9:Mod_R, 10:Ans_R, 11:FB_R, 12:Cost_R
                ts = row.iloc[0]
                q = row.iloc[2]
                
                # Filter Logic
                if search_query and (search_query not in str(q).lower()):
                    continue
                
                count += 1
                
                # Card Header
                header_text = f"🕒 {ts} | ❓ {q[:50]}..." if len(str(q)) > 50 else f"🕒 {ts} | ❓ {q}"
                
                with st.expander(header_text, expanded=False):
                    st.markdown(f"**Question:** {q}")
                    st.markdown("---")
                    
                    hc1, hc2 = st.columns(2)
                    
                    # --- Left History ---
                    with hc1:
                        kb_l = row.iloc[3]
                        mod_l = row.iloc[4]
                        ans_l = row.iloc[5]
                        fb_l = row.iloc[6]
                        cost_l = row.iloc[7]
                        
                        st.markdown(f"👈 **Left Side**")
                        st.caption(f"🛠 {mod_l} | 📚 {kb_l}")
                        st.info(ans_l)
                        
                        # Added Copy Button for History
                        render_copy_button(ans_l, f"copy_hist_l_{index}")
                        
                        st.caption(f"💸 {cost_l} THB | Feedback: {fb_l if fb_l else '-'}/5")

                    # --- Right History ---
                    with hc2:
                        kb_r = row.iloc[8]
                        mod_r = row.iloc[9]
                        ans_r = row.iloc[10]
                        fb_r = row.iloc[11]
                        cost_r = row.iloc[12]
                        
                        st.markdown(f"👉 **Right Side**")
                        st.caption(f"🛠 {mod_r} | 📚 {kb_r}")
                        st.success(ans_r)
                        
                        # Added Copy Button for History
                        render_copy_button(ans_r, f"copy_hist_r_{index}")
                        
                        st.caption(f"💸 {cost_r} THB | Feedback: {fb_r if fb_r else '-'}/5")

            except Exception as e:
                # Skip malformed rows
                continue

        if count == 0:
            st.warning("ไม่พบข้อมูลที่ค้นหา")
            
    else: 
        st.info("ไม่พบประวัติการใช้งาน")
