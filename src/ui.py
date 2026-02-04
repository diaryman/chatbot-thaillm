import streamlit as st
import html

# ==========================================
# 🎨 THEME & CSS
# ==========================================

def load_custom_css(theme_mode="Modern Dark"):
    """
    Injects custom CSS based on the selected theme without Bootstrap.
    Uses Custom Utility Classes.
    """
    if "Light" in theme_mode:
        bg_image = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        text_color = "#1e293b"
        
        # Premium Glass Light
        glass_bg = "rgba(255, 255, 255, 0.7)"
        glass_border = "1px solid rgba(255, 255, 255, 0.8)"
        glass_shadow = "0 20px 40px rgba(0, 0, 0, 0.05)"
        
        header_gradient = "linear-gradient(to right, #243949 0%, #517fa4 100%)"
        user_bubble_bg = "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)" 
        user_bubble_text = "#ffffff"
        
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        input_bg = "rgba(255, 255, 255, 1)"
        accent_color = "#2563eb"
        
    else: # Dark Mode
        bg_image = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)" 
        text_color = "#f1f5f9"
        
        # Premium Glass Dark
        glass_bg = "rgba(30, 41, 59, 0.7)"
        glass_border = "1px solid rgba(255, 255, 255, 0.08)"
        glass_shadow = "0 20px 40px rgba(0, 0, 0, 0.4)"
        
        header_gradient = "linear-gradient(135deg, #1e293b 0%, #334155 100%)"
        user_bubble_bg = "linear-gradient(135deg, #475569 0%, #1e293b 100%)"
        user_bubble_text = "#f1f5f9"
        
        sidebar_bg = "rgba(15, 23, 42, 0.95)"
        input_bg = "rgba(30, 41, 59, 1)"
        accent_color = "#60a5fa"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset */
        .stApp {{ background-image: {bg_image}; background-attachment: fixed; background-size: cover; }}
        html, body, [class*="css"], .stMarkdown, .stText, p, ol, ul, li {{ 
            font-family: 'Inter', 'Sarabun', sans-serif !important; 
            color: {text_color} !important; 
        }}
        h1, h2, h3, h4, h5, h6 {{ 
            font-family: 'Inter', 'Sarabun', sans-serif !important; 
            font-weight: 700 !important;
            color: {text_color} !important; 
            letter-spacing: -0.02em;
        }}
        
        /* Glassmorphism Classes */
        .glass-card {{
            background: {glass_bg} !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: {glass_border} !important;
            box-shadow: {glass_shadow} !important;
            border-radius: 20px !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }}
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 30px 60px rgba(0,0,0,0.12) !important;
        }}
        
        /* Utility Classes */
        .d-flex {{ display: flex; }}
        .align-items-center {{ align-items: center; }}
        .justify-content-between {{ justify-content: space-between; }}
        .justify-content-end {{ justify-content: flex-end; }}
        .gap-2 {{ gap: 0.5rem; }}
        .mb-2 {{ margin-bottom: 0.5rem; }}
        .mb-4 {{ margin-bottom: 1.5rem; }}
        .me-2 {{ margin-right: 0.5rem; }}
        
        .badge {{
            display: inline-block;
            padding: 0.45em 0.85em;
            font-size: 0.75em;
            font-weight: 600;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 50px;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .bg-light {{ background-color: rgba(255,255,255,0.1); color: {text_color} !important; border: 1px solid rgba(255,255,255,0.1); }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Header */
        .court-header {{ 
            background: {header_gradient}; 
            padding: 2.5rem; border-radius: 24px; color: white !important; 
            text-align: center; margin-bottom: 30px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            animation: fadeIn 0.8s ease-out;
            position: relative;
            overflow: hidden;
        }}
        .court-header::after {{
            content: "";
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.05), transparent);
            transform: rotate(45deg);
            pointer-events: none;
        }}
        .court-icon {{ font-size: 60px; filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3)); }}
        
        /* Response Card Structure */
        .response-card-container {{
            background: {glass_bg} !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 20px; 
            box-shadow: {glass_shadow};
            margin-bottom: 25px; 
            overflow: hidden; 
            border: {glass_border};
            animation: fadeIn 0.5s ease-out;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .response-card-container:hover {{
            border-color: {accent_color}50;
            transform: scale(1.01);
        }}
        
        .card-header-custom {{ 
            padding: 16px 24px; 
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex; justify-content: space-between; align-items: center; 
        }}
        
        .card-body-custom {{ 
            padding: 24px 28px; 
            font-size: 1rem;
            line-height: 1.7;
        }}
        
        .model-badge {{ 
            display: inline-flex; align-items: center;
            padding: 8px 16px; border-radius: 30px; 
            font-size: 0.9rem; font-weight: 700; 
            color: white !important; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* User Bubble */
        .user-bubble {{ 
            background: {user_bubble_bg}; 
            color: {user_bubble_text} !important; 
            padding: 18px 26px; 
            border-radius: 24px 24px 4px 24px; 
            margin-left: auto; width: fit-content; max-width: 80%; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            font-weight: 500;
        }}
        
        /* Streamlit Element Overrides */
        div[data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            border-right: 1px solid rgba(255,255,255,0.05);
        }}
        .stChatInput textarea {{ 
            background-color: {input_bg} !important; 
            border-radius: 30px !important; 
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 15px 25px !important;
        }}
        
        /* Stats Cards */
        .stat-card {{
            padding: 20px;
            text-align: center;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
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
        <div style="text-align: center; padding: 40px; animation: slideIn 1s ease-out;">
            <div style="font-size: 4rem; color: #667eea; margin-bottom: 20px;">💬</div>
            <h3>ยินดีต้อนรับสู่ Smart Court AI</h3>
            <p style="opacity: 0.8;">เริ่มต้นใช้งานโดยเลือกคำถามตัวอย่าง หรือพิมพ์คำถามของคุณที่ด้านล่าง</p>
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
