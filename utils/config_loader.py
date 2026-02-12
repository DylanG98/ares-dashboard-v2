import json
import os
import toml

def load_config(config_path="config.json"):
    """
    Loads configuration from:
    1. config.json (Local file) - Priority
    2. .streamlit/secrets.toml (Local development)
    3. st.secrets (Streamlit Cloud)
    """
    config = {"watchlist": [], "telegram": {}}

    # 1. Try Local JSON (Primary for Local Run)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Error loading {config_path}: {e}")

    # 2. Try Streamlit Secrets (Cloud / Fallback)
    try:
        import streamlit as st
        # Convert to dict to ensure compatibility
        # st.secrets behaves like a dict but we want a standard mutable dict
        secrets = dict(st.secrets)
        
        # Parse nested sections if they are not already dicts (Streamlit handles toml parsing automatically, but good to ensure)
        # Deep merge/copy might be needed if structure is complex, but basic dict(st.secrets) usually suffices for top level
        
        # Normalize keys if needed or merge with defaults
        # Assume st.secrets has the same structure
        return secrets
        
    except Exception:
        # Streamlit might not be installed or no secrets found
        pass

    return config

def save_config(config, config_path="config.json"):
    """
    Saves configuration. 
    NOTE: This only works for LOCAL file system. 
    Streamlit Cloud secrets are read-only at runtime.
    """
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
