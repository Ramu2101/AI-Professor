# AI Professor - Virtual AI Classroom

Production-ready Streamlit app with robust API key loading, modular architecture, and cached generation/video services.

## Project Structure

```text
ai_professor/
  app.py
  services/
    gemini_service.py
    youtube_service.py
  components/
    layout.py
    diagram.py
  utils/
    env.py
app.py
requirements.txt
.env.example
```

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

1. Deploy this repo from GitHub.
2. In Streamlit Cloud: App Settings -> Secrets.
3. Add:

```toml
GEMINI_API_KEY="your_gemini_api_key"
YOUTUBE_API_KEY="your_youtube_api_key"
```

The app reads `st.secrets` first and falls back to local `os.getenv` for development.