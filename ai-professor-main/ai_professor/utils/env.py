from __future__ import annotations

import os

import streamlit as st

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


def load_local_env() -> None:
    """Load local .env for development. Streamlit Cloud uses st.secrets."""
    if load_dotenv is not None:
        load_dotenv()


def get_api_key(key_name: str) -> str | None:
    """Read key from Streamlit secrets first, then fallback to local environment."""
    try:
        if key_name in st.secrets:
            value = st.secrets[key_name]
            if isinstance(value, str) and value.strip():
                return value.strip()
    except Exception:
        pass

    env_value = os.getenv(key_name)
    if isinstance(env_value, str) and env_value.strip():
        return env_value.strip()

    return None


def require_api_key(key_name: str, message: str) -> str:
    key = get_api_key(key_name)
    if not key:
        st.error(message)
        st.stop()
    return key