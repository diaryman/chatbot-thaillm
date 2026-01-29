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
        bg_image = "linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%)"
        text_color = "#1a1a1a"
        
        # Glassmorphism Light
        glass_bg = "rgba(255, 255, 255, 0.90)"
        glass_border = "1px solid rgba(0, 0, 0, 0.1)"
        glass_shadow = "0 8px 32px 0 rgba(31, 38, 135, 0.10)"
        
        header_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        user_bubble_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" 
        user_bubble_text = "#ffffff"
        
        sidebar_bg = "#ffffff"
        input_bg = "rgba(255, 255, 255, 0.9)"
        
    else: # Dark Mode
        bg_image = "linear-gradient(to top, #09203f 0%, #537895 100%)" 
        text_color = "#f0f2f6"
        
        # Glassmorphism Dark
        glass_bg = "rgba(25, 25, 35, 0.85)"
        glass_border = "1px solid rgba(255, 255, 255, 0.15)"
        glass_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.3)"
        
        header_gradient = "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)"
        user_bubble_bg = "rgba(60, 64, 67, 0.8)"
        user_bubble_text = "#ffffff"
        
        sidebar_bg = "#0e1117"
        input_bg = "rgba(40, 44, 52, 0.8)"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset */
        .stApp {{ background-image: {bg_image}; background-attachment: fixed; background-size: cover; }}
        html, body, [class*="css"], .stMarkdown, .stText, p, ol, ul, li {{ font-family: 'Sarabun', sans-serif !important; color: {text_color} !important; }}
        h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; }}
        
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
            padding: 0.35em 0.65em;
            font-size: 0.75em;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.375rem;
            color: #fff;
        }}
        .bg-light {{ background-color: #f8f9fa; color: #212529 !important; border: 1px solid #dee2e6; }}
        .bg-warning {{ background-color: #ffc107; color: #000 !important; }}
        
        /* Animations */
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Header */
        .court-header {{ 
            background: {header_gradient}; 
            padding: 2rem; border-radius: 16px; color: white !important; 
            text-align: center; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            animation: slideIn 0.8s ease-out;
        }}
        .court-icon {{ font-size: 80px; }}
        
        /* Response Card Structure */
        .response-card-container {{
            background: #ffffff;
            border-radius: 16px; 
            box-shadow: {glass_shadow};
            margin-bottom: 20px; 
            overflow: hidden; 
            animation: slideIn 0.5s ease-out;
        }}
        
        .card-header-custom {{ 
            background: rgba(0,0,0,0.02); 
            padding: 12px 20px; 
            border-bottom: 1px solid rgba(0,0,0,0.05);
            display: flex; justify-content: space-between; align-items: center; 
        }}
        
        .card-body-custom {{ 
            padding: 20px 25px; 
            color: #212529 !important; /* Force Dark Text */
        }}
        
        /* Inner Markdown Styling */
        .card-body-custom p {{ margin-bottom: 0.8rem; line-height: 1.6 !important; }}
        .card-body-custom li {{ margin-bottom: 0.5rem; line-height: 1.6 !important; }}
        .card-body-custom ol, .card-body-custom ul {{ padding-left: 1.5rem; margin-bottom: 1rem; }}
        
        .model-badge {{ 
            display: inline-flex; align-items: center;
            padding: 6px 14px; border-radius: 20px; 
            font-size: 0.85rem; font-weight: 600; 
            color: white !important; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        /* User Bubble */
        .user-bubble {{ 
            background: {user_bubble_bg}; 
            color: {user_bubble_text} !important; 
            padding: 15px 22px; 
            border-radius: 20px 20px 5px 20px; 
            margin-left: auto; width: fit-content; max-width: 85%; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }}
        
        /* Inputs */
        .stChatInput textarea {{ background-color: {input_bg} !important; border-radius: 25px !important; }}
        
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

def render_result_card(res_data, kb_name):
    """
    Renders result card using Split HTML approach + Native Markdown.
    This ensures lists and formatting are rendered correctly by Streamlit.
    """
    icon = res_data['config']['icon']
    color = res_data['config']['color']
    model_name = res_data['model']
    
    badge_style = f"background: linear-gradient(135deg, {color}, #555);"
    # Full border with color tint + thick left accent
    border_style = f"border: 1px solid {color}80; border-left: 6px solid {color}; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
    
    # 1. Opening Card & Header
    st.markdown(f"""
    <div class="response-card-container" style="{border_style}">
        <div class="card-header-custom" style="background: {color}10;">
            <div class="d-flex align-items-center">
                <span style="font-size: 1.5rem; margin-right: 10px;">{icon}</span>
                <span class="model-badge" style="{badge_style}">{model_name}</span>
            </div>
            <span class="badge bg-light" style="color:#555 !important;"><i class="bi bi-stopwatch"></i> {res_data['time']:.2f}s</span>
        </div>
        <div class="card-body-custom">
            <div class="mb-2" style="font-size: 0.9rem; color: #666; border-bottom: 1px dashed #eee; padding-bottom: 5px; margin-bottom: 10px;">
                📁 {kb_name}
            </div>
    """, unsafe_allow_html=True)
    
    # 2. Native Markdown Content (Fixes List Alignment & Formatting)
    st.markdown(res_data['answer'])
    
    # 3. Closing Divs
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 4. Citations
    if res_data.get("citations"):
        with st.expander(f"📚 เอกสารอ้างอิง ({len(res_data['citations'])})"):
            for fname, snippet in res_data['citations'].items():
                st.caption(f"**{fname}**")
                st.info(snippet)

    # 5. Footer Cost
    st.markdown(f"""
        <div class="d-flex justify-content-end" style="padding: 10px; background: rgba(0,0,0,0.03); font-size: 0.8rem; color: #888; border-radius: 0 0 16px 16px; margin-top: -20px; position: relative; z-index: 1;">
            💰 Cost: {res_data['cost']:.4f} THB
        </div>
    """, unsafe_allow_html=True)
