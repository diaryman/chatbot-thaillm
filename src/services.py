# src/services.py
import json
import time
import requests
import os
import streamlit as st

from src.config import REGION, MODELS, SYSTEM_PROMPT, THB_RATE, MODEL_PRICING
from src.utils import load_secret

# Initialize Secrets
AWS_ACCESS_KEY = load_secret("AWS_ACCESS_KEY")
AWS_SECRET_KEY = load_secret("AWS_SECRET_KEY")
THAILLM_API_KEY = load_secret("THAILLM_API_KEY")

# ==========================================
# 🔌 CLIENT FACTORIES
# ==========================================

@st.cache_resource
def get_aws_agent():
    """AWS Bedrock Agent for Knowledge Base retrieval."""
    if not AWS_ACCESS_KEY: return None
    import boto3
    return boto3.client(
        'bedrock-agent-runtime', 
        region_name=REGION, 
        aws_access_key_id=AWS_ACCESS_KEY, 
        aws_secret_access_key=AWS_SECRET_KEY
    )

# ==========================================
# 🧠 LOGIC FUNCTIONS
# ==========================================

def retrieve_context(query, kb_id):
    """Retrieves relevant context from AWS Bedrock Knowledge Base."""
    if not kb_id: 
        return "", {}
    
    agent = get_aws_agent()
    if not agent: 
        return "", {}

    try:
        res = agent.retrieve(
            knowledgeBaseId=kb_id, 
            retrievalQuery={'text': query}, 
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 5}}
        )
        ctx = ""
        citation_details = {}
        
        if 'retrievalResults' in res:
            for r in res['retrievalResults']:
                text_chunk = r['content']['text']
                ctx += f"- {text_chunk}\n"
                
                # Extract filename safely
                uri = r.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
                fname = uri.split('/')[-1]
                
                if fname not in citation_details:
                    citation_details[fname] = text_chunk[:200].replace('\n', ' ') + "..."
                    
        return ctx, citation_details
    except Exception as e: 
        print(f"KB Error ({kb_id}): {e}")
        return "", {}

def calculate_cost(model_id, full_text_in, full_text_out):
    """Estimates cost in THB."""
    pricing = MODEL_PRICING.get(model_id, [0, 0])
    in_tokens = len(full_text_in) / 3.0 
    out_tokens = len(full_text_out) / 3.0
    cost = (in_tokens/1e6 * pricing[0]) + (out_tokens/1e6 * pricing[1])
    return cost * THB_RATE

def call_single_model(model_name, prompt, context, citations_dict, temperature=0.5):
    """Invokes a single AI model."""
    cfg = MODELS[model_name]
    full_input = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Question: {prompt}"
    answer = ""
    start_time = time.time()
    
    try:
        # --- ThaiLLM API ---
        if cfg["type"] == "thaillm":
            if not THAILLM_API_KEY: 
                raise ValueError("ThaiLLM API Key missing")
            
            headers = {
                "Content-Type": "application/json",
                "apikey": THAILLM_API_KEY
            }
            
            payload = {
                "model": "/model",  # ThaiLLM expects this exact value
                "messages": [
                    {"role": "user", "content": full_input}
                ],
                "max_tokens": 2048,
                "temperature": temperature
            }
            
            # Make API request
            response = requests.post(
                cfg["endpoint"],
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Remove <think> tags content
                import re
                answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
                
            else:
                # Include more debugging info
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise ValueError(error_msg)
            
    except Exception as e:
        answer = f"⚠️ Error: {str(e)}"
    
    elapsed = time.time() - start_time
    
    # Get model key for pricing
    model_key = model_name.lower().split()[0]  # Extract first word for pricing key
    
    return {
        "model": model_name, 
        "answer": answer, 
        "citations": citations_dict, 
        "cost": calculate_cost(model_key, full_input, answer), 
        "config": cfg, 
        "time": elapsed
    }

def generate_related_questions(query, context, model_name="Typhoon"):
    """
    Generates 3 related follow-up questions based on the context.
    Uses user-selected model or falls back to OpenThaiGPT.
    """
    try:
        # Rely on global imports for MODELS and THAILLM_API_KEY
        import streamlit as st # For debugging
        
        # 1. Select Model
        # User requested Typhoon for suggestions
        target_model_key = None
        for k in MODELS.keys():
            if "Typhoon" in k:
                target_model_key = k
                break
        
        # Fallback to OpenThaiGPT if Typhoon missing
        if not target_model_key:
             for k in MODELS.keys():
                if "OpenThaiGPT" in k:
                    target_model_key = k
                    break
        
        # Final fallback
        if not target_model_key:
            target_model_key = list(MODELS.keys())[0]

        cfg = MODELS[target_model_key]
        
        # 2. Prepare Request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {THAILLM_API_KEY}",
            "apikey": THAILLM_API_KEY
        }
        
        prompt = f"""
        Instructions:
        Based on the user's question and context, suggest 3 RELEVANT and VERY SHORT follow-up questions in Thai.
        
        Strict Rules:
        1. NO <think> tags. Output ONLY the questions.
        2. Questions must be under 10 words.
        3. No numbering (e.g. 1.), no bullets.
        4. Focus on Administrative Court procedures.

        Context: {context[:500]}...
        User Question: {query}
        
        Suggested Questions:
        """
        
        # Use "/model" as expected by ThaiLLM API (same as call_single_model)
        model_id_for_payload = "/model"

        payload = {
            "model": model_id_for_payload, 
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        # 3. Call API
        # Increased timeout to 20s
        response = requests.post(cfg["endpoint"], headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Remove <think> tags
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            # Robust Parsing
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            questions = []
            for line in lines:
                # Remove common prefixes like "1.", "-", "*"
                clean = re.sub(r'^[\d\-\*\.]+\s*', '', line)
                if len(clean) > 5: # Min length check
                    questions.append(clean)
            
            return questions[:3]
            
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            st.error(f"Suggestion API Error: {response.status_code}")
            st.session_state.setdefault("system_logs", []).append(f"❌ Suggestion API Error: {error_msg}")
            return []
            
    except Exception as e:
        import streamlit as st
        st.error("Suggestion System Error")
        st.session_state.setdefault("system_logs", []).append(f"❌ Suggestion Exception: {str(e)}")
        return []
