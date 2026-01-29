# src/utils.py
import streamlit as st
import os

def load_secret(key_name: str, default: str = "") -> str:
    """
    Load a secret from Streamlit secrets or environment variables.
    
    Args:
        key_name (str): The key to look for in secrets.
        default (str): Default value if not found.
        
    Returns:
        str: The secret value.
    """
    # 1. Try streamlit secrets
    try:
        return st.secrets[key_name]
    except (FileNotFoundError, KeyError):
        pass
        
    # 2. Try environment variables
    env_val = os.getenv(key_name)
    if env_val:
        return env_val
        
    # 3. Return default
    return default

def check_secrets():
    """Validates that critical secrets are present."""
    required_keys = ["AWS_ACCESS_KEY", "AWS_SECRET_KEY"]
    missing = [key for key in required_keys if not load_secret(key)]
    
    if missing:
        st.error(f"❌ Missing critical secrets: {', '.join(missing)}. Please add them to .streamlit/secrets.toml")
        st.stop()
