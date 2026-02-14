# AI Professor (Streamlit)

Production-ready, modular Streamlit app for structured AI learning.

## Structure

```text
ai_professor/
  app.py
  services/
    gemini_service.py
    youtube_service.py
  utils/
    formatting.py
app.py
requirements.txt
.env.example
```

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud secrets

Add in Streamlit Cloud app settings:

- GEMINI_API_KEY
- YOUTUBE_API_KEY

The app reads secrets from `st.secrets` first, then falls back to environment variables for local development.