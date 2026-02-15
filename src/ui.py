import streamlit as st
import html

# ==========================================
# 🎨 THEME & CSS
# ==========================================

def load_custom_css(theme_mode="Official Light"):
    """
    Injects custom CSS based on the selected theme.
    Handles Light and Dark modes with explicit overrides for Streamlit elements.
    """
    if "Light" in theme_mode:
        # --- OFFICIAL LIGHT THEME VARIABLES ---
        colors = {
            "bg_app": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
            "bg_sidebar": "#ffffff",
            "text_main": "#0f172a",       # Slate 900
            "text_sidebar": "#334155",    # Slate 700
            "input_bg": "#ffffff",
            "input_border": "1px solid #94a3b8", # DEFINED STRONGER BORDER
            "input_text": "#0f172a",
            "button_bg": "#ffffff",
            "button_text": "#0f172a",
            "button_border": "1px solid #94a3b8", # DEFINED STRONGER BORDER
            "glass_bg": "rgba(255, 255, 255, 0.95)",
            "glass_border": "1px solid #cbd5e1", # DEFINED CARD BORDER
            "glass_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "header_gradient": "linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)",
            "accent": "#1e40af",
            "user_bubble_bg": "#eff6ff",  
            "user_bubble_text": "#1e3a8a" 
        }
    else:
        # --- MODERN DARK THEME VARIABLES ---
        colors = {
            "bg_app": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
            "bg_sidebar": "rgba(15, 23, 42, 0.95)",
            "text_main": "#f8fafc",       
            "text_sidebar": "#e2e8f0",    
            "input_bg": "rgba(30, 41, 59, 0.6)",
            "input_border": "1px solid rgba(255, 255, 255, 0.2)", # STRONGER BORDER
            "input_text": "#f8fafc",
            "button_bg": "rgba(255, 255, 255, 0.05)",
            "button_text": "#f8fafc",
            "button_border": "1px solid rgba(255, 255, 255, 0.15)", # STRONGER BORDER
            "glass_bg": "rgba(30, 41, 59, 0.7)",
            "glass_border": "1px solid rgba(255, 255, 255, 0.15)", # STRONGER CARD BORDER
            "glass_shadow": "0 20px 40px rgba(0, 0, 0, 0.4)",
            "header_gradient": "linear-gradient(135deg, #1e40af 0%, #172554 100%)",
            "accent": "#60a5fa",
            "user_bubble_bg": "#1e293b",
            "user_bubble_text": "#f8fafc"
        }

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap');
        
        /* --- GLOBAL & APP BACKGROUND --- */
        .stApp {{
            background: {colors['bg_app']} !important;
            background-attachment: fixed !important;
            background-size: cover !important;
        }}
        
        /* Safer selector to avoid breaking icons */
        .stApp {{
             font-family: 'Inter', 'Sarabun', sans-serif !important;
        }}
        
        h1, h2, h3, h4, h5, h6, p, li, .stMarkdown, .stText, input, textarea, button {{
            font-family: 'Inter', 'Sarabun', sans-serif !important;
            color: {colors['text_main']} !important;
        }}
        
        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {{
            background-color: {colors['bg_sidebar']} !important;
            border-right: 1px solid rgba(0,0,0,0.05) !important;
            box-shadow: 10px 0 30px rgba(0,0,0,0.02) !important; /* Soft Shadow Separator */
        }}
        section[data-testid="stSidebar"] .stMarkdown p, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] span {{
            color: {colors['text_sidebar']} !important;
        }}
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
             color: {colors['text_sidebar']} !important;
        }}
        
        /* --- INPUTS --- */
        /* --- INPUTS --- */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stTextArea"] textarea, 
        div[data-testid="stNumberInput"] input,
        .stChatInput textarea {{
            background-color: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
            caret-color: {colors['input_text']} !important;
            border: {colors['input_border']} !important;
            border-radius: 16px !important; /* Modern Rounded Corners */
            padding: 12px 16px !important;
            transition: border 0.2s ease;
        }}
        
        div[data-testid="stTextInput"] input:focus, 
        div[data-testid="stTextArea"] textarea:focus, 
        div[data-testid="stNumberInput"] input:focus, 
        .stChatInput textarea:focus {{
            border-color: {colors['accent']} !important;
            box-shadow: 0 0 0 2px {colors['accent']}20 !important;
        }}
        
        div[data-baseweb="select"] > div {{
            background-color: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
            border: {colors['input_border']} !important;
            border-radius: 16px !important;
        }}
        
        /* MULTI-SELECT TAGS (PILLS) FIX */
        span[data-baseweb="tag"], div[data-testid="stMultiSelectTag"] {{
            background-color: {colors['accent']} !important;
            border-radius: 8px !important;
        }}
        span[data-baseweb="tag"] span, 
        div[data-testid="stMultiSelectTag"] span,
        div[data-testid="stMultiSelectTag"] p {{
            color: white !important;
        }}
        /* Icon (X) for tags */
        span[data-baseweb="tag"] svg, div[data-testid="stMultiSelectTag"] svg {{
            fill: white !important;
        }}

        div[data-baseweb="menu"] {{
            background-color: {colors['bg_sidebar']} !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1) !important;
        }}
        div[data-baseweb="option"] {{
             color: {colors['input_text']} !important;
        }}
        div[data-baseweb="option"]:hover {{
             background-color: {colors['accent']}20 !important;
        }}

        /* --- BUTTONS --- */
        .stButton > button {{
            background-color: {colors['button_bg']} !important;
            color: {colors['button_text']} !important;
            border: {colors['button_border']} !important;
            border-radius: 24px !important; /* Pill Shape */
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }}
        .stButton > button:hover {{
            border-color: {colors['accent']} !important;
            color: {colors['accent']} !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
        }}
        
        /* --- CARDS (Glassmorphism) --- */
        .glass-card, .response-card-container {{
            background: {colors['glass_bg']} !important;
            border: {colors['glass_border']} !important;
            box-shadow: {colors['glass_shadow']} !important;
            border-radius: 24px !important; /* Modern Large Radius */
            overflow: hidden; 
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; /* Smooth Hover Physics */
        }}
        
        .glass-card:hover, .response-card-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
            border-color: {colors['accent']}40 !important;
        }}
        
        /* --- HEADERS --- */
        .court-header {{
            background: {colors['header_gradient']} !important;
            color: white !important;
            padding: 3rem 2rem;
            border-radius: 32px; /* Very Rounded Header */
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
            text-align: center;
            margin-bottom: 2.5rem;
            position: relative;
            overflow: hidden;
            animation: fadeIn 0.8s ease-out;
        }}
        .court-header h2, .court-header p, .court-header .court-icon {{
            color: white !important;
        }}
        
        /* --- USER BUBBLE --- */
        .user-bubble {{
            background-color: {colors['user_bubble_bg']} !important;
            color: {colors['user_bubble_text']} !important;
            padding: 1rem 1.5rem;
            border-radius: 20px 20px 4px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            font-weight: 500;
        }}
        .user-bubble p {{
             color: {colors['user_bubble_text']} !important;
        }}
        
        /* --- DIVIDERS --- */
        hr {{
            margin: 2rem 0 !important;
            border: 0 !important;
            border-top: 1px solid {colors['input_border']} !important;
            opacity: 0.5 !important;
        }}
        
        /* --- UTILS & OVERRIDES --- */
        code {{
            color: #d63384 !important;
            background-color: rgba(0,0,0,0.05) !important;
            border-radius: 4px;
            padding: 2px 4px;
        }}
        
        /* Remove default Streamlit Header Decoration */
        header[data-testid="stHeader"] {{
            background-color: transparent !important; 
        }}
        
        /* Fix Expander Background (Crucial for Light Mode) */
        .stExpander, div[data-testid="stExpander"] {{
            background-color: transparent !important;
            border: none !important;
            color: {colors['text_main']} !important;
        }}
        
        .streamlit-expanderHeader, div[data-testid="stExpander"] > details > summary {{
            background-color: {colors['input_bg']} !important;
            color: {colors['text_main']} !important;
            border: 1px solid {colors['input_border']} !important;
            border-radius: 8px !important;
        }}
        
        /* Force Text Color inside Expander Header */
        .streamlit-expanderHeader p, 
        div[data-testid="stExpander"] > details > summary p,
        div[data-testid="stExpander"] > details > summary span {{
            color: {colors['text_main']} !important;
            font-weight: 600;
        }}
        
        /* Fix Expander Icon Color to match text */
        div[data-testid="stExpander"] > details > summary svg {{
            fill: {colors['text_main']} !important;
            color: {colors['text_main']} !important; 
        }}
        
        /* Model Badge Text */
        .model-badge {{
            color: white !important;
            display: inline-flex; align-items: center;
            padding: 8px 16px; border-radius: 30px; 
            font-size: 0.9rem; font-weight: 700; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .card-header-custom {{
             padding: 16px 24px; 
             border-bottom: 1px solid rgba(0,0,0,0.05);
             display: flex; justify-content: space-between; align-items: center; 
        }}
        .card-body-custom {{
             padding: 24px 28px; 
             font-size: 1rem;
             line-height: 1.7;
        }}
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
        <div class="court-header">
            <div class="court-icon">⚖️</div>
            <h2 style="margin: 10px 0;">Smart Court AI Assistant</h2>
            <p style="opacity: 0.9;">ผู้ช่วยอัจฉริยะศาลปกครอง ตอบทุกข้อสงสัยด้วย AI</p>
        </div>
    """, unsafe_allow_html=True)

def render_welcome_screen():
    st.markdown("""
        <div style="text-align: center; padding: 40px; animation: fadeIn 1s ease-out;">
            <div style="font-size: 4rem; color: #3b82f6; margin-bottom: 20px;">💬</div>
            <h2 style="margin-bottom: 10px;">ยินดีต้อนรับสู่ Smart Court AI</h2>
            <p style="opacity: 0.9; font-size: 1.1rem;">
                เริ่มต้นใช้งานโดยเลือกคำถามตัวอย่าง หรือพิมพ์คำถามของคุณที่ด้านล่าง<br/>
                <b>ระบบจะวิเคราะห์คำถามและให้คำตอบโดยอิงจากฐานข้อมูลกฎหมายปกครอง</b>
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_user_message(content):
    safe_content = html.escape(content)
    st.markdown(f"""
        <div class="d-flex justify-content-end mb-4">
            <div class="user-bubble">
                {safe_content}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_copy_button(text_to_copy, unique_key):
    """
    Renders a small Copy button using Javascript.
    """
    safe_text = text_to_copy.replace("'", "\\'").replace("\n", "\\n").replace('"', '\\"')
    
    html_code = f"""
    <div style="display: flex; justify-content: flex-end; margin-top: 5px;">
        <button onclick="copyToClipboard_{unique_key}()" style="
            background: transparent; border: 1px solid #ccc; border-radius: 15px; 
            padding: 5px 12px; font-size: 0.8rem; cursor: pointer; color: #666;">
            📋 Copy
        </button>
        <span id="msg_{unique_key}" style="margin-left: 10px; color: green; font-size: 0.8rem; display: none;">
            ✅ Copied!
        </span>
    </div>

    <script>
    function copyToClipboard_{unique_key}() {{
        const text = '{safe_text}';
        navigator.clipboard.writeText(text).then(function() {{
            const msg = document.getElementById('msg_{unique_key}');
            msg.style.display = 'inline';
            setTimeout(function() {{ msg.style.display = 'none'; }}, 2000);
        }}, function(err) {{
            console.error('Async: Could not copy text: ', err);
        }});
    }}
    </script>
    """
    st.components.v1.html(html_code, height=40)

def render_sidebar_header(username):
    st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 50px; margin-bottom: 10px;">⚖️</div>
            <h3 style="margin: 0;">Smart Court AI</h3>
            <p style="font-size: 0.8rem; opacity: 0.7;">User: <b>{username}</b></p>
        </div>
        <hr style="margin: 10px 0; opacity: 0.1;"/>
    """, unsafe_allow_html=True)

def render_result_card(res_data, kb_name):
    """
    Renders result card using Split HTML approach + Native Markdown.
    Updated with glassmorphism and better animations.
    """
    icon = res_data['config']['icon']
    color = res_data['config']['color']
    model_name = res_data['model']
    
    badge_style = f"background: linear-gradient(135deg, {color}, #555);"
    border_style = f"border-left: 5px solid {color};"
    
    # 1. Opening Card & Header
    st.markdown(f"""
    <div class="response-card-container" style="{border_style}">
        <div class="card-header-custom" style="background: {color}15;">
            <div class="d-flex align-items-center">
                <span style="font-size: 1.4rem; margin-right: 12px;">{icon}</span>
                <span class="model-badge" style="{badge_style}">{model_name}</span>
            </div>
            <div class="d-flex align-items-center gap-2">
                <span class="badge bg-light" style="font-size: 0.7rem;">
                    ⏱️ {res_data['time']:.1f}s
                </span>
            </div>
        </div>
        <div class="card-body-custom">
            <div style="font-size: 0.8rem; opacity: 0.6; margin-bottom: 15px; display: flex; align-items: center; gap: 5px;">
                <span>📂</span> {kb_name}
            </div>
    """, unsafe_allow_html=True)
    
    # 2. Native Markdown Content
    st.markdown(res_data['answer'])
    
    # 3. Closing Divs
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 4. Citations
    if res_data.get("citations"):
        with st.expander(f"📚 Sources ({len(res_data['citations'])})", expanded=False):
            for fname, snippet in res_data['citations'].items():
                st.markdown(f"**📄 {fname}**")
                st.caption(snippet)
    
    # 5. Footer Cost
    st.markdown(f"""
        <div style="padding: 12px 24px; background: rgba(0,0,0,0.02); font-size: 0.75rem; color: #888; border-top: 1px solid rgba(0,0,0,0.03); display: flex; justify-content: space-between;">
            <span>Token Usage: Optimized</span>
            <span>Fee: {res_data['cost']:.4f} THB</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
