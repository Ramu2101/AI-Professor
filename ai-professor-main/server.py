import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
# Try loading .env.local first (Vite convention), then .env
load_dotenv(".env.local")
load_dotenv()

app = FastAPI(title="AI Professor Backend")

# CORS Configuration
# CRITICAL: Allowing requests from the Vite Frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

print("--- SERVER DEBUG INFO ---")
print(f"Loading from .env.local: {os.path.exists('.env.local')}")
print(f"GEMINI_API_KEY Found: {bool(GEMINI_API_KEY)}")
print(f"YOUTUBE_API_KEY Found: {bool(YOUTUBE_API_KEY)}")
print("-------------------------")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Data Models ---
class StudentQuestion(BaseModel):
    question: str

class ProfessorContent(BaseModel):
    definition: str
    key_notes: list[str]
    application: str

class LectureResponse(BaseModel):
    answer: ProfessorContent
    video_id: str | None = None

@app.post("/ask", response_model=LectureResponse)
async def ask_professor(request: StudentQuestion):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI Service unavailable (API Key missing).")

    try:
        # 1. Ask Gemini
        # Prompting for specific keys: definition, key_notes, application
        # Using gemini-flash-latest for better stability/quota management
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Explain this topic in detail for a curious undergraduate student: '{request.question}'.
        Return a valid JSON object with exactly these keys:
        - "definition": A thorough explanation (at least 180 words) covering what it is, how it works, and why it matters.
        - "key_notes": A list of 8-12 distinct, information-dense bullet points. Each bullet should be 1-2 complete sentences.
        - "application": A detailed practical explanation (at least 140 words) including realistic real-world examples, trade-offs, and limitations.

        Rules:
        - Be specific and educational, not generic.
        - Prefer concrete examples over abstract statements.
        - Keep language clear, but do not oversimplify.
        - Output JSON only.
        """
        
        try:
            response = model.generate_content(
                contents=prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.35,
                    "max_output_tokens": 2048,
                }
            )
        except Exception as gemini_error:
            print(f"Gemini Generation Error: {gemini_error}")
            raise HTTPException(status_code=503, detail=f"AI Service Error: {str(gemini_error)}")
        
        # Parse Gemini Response
        ai_data = json.loads(response.text)
        
        # 2. Search YouTube
        # Query: question + educational
        video_id = None
        if YOUTUBE_API_KEY:
            try:
                search_query = f"{request.question} educational"
                yt_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': search_query,
                    'key': YOUTUBE_API_KEY,
                    'type': 'video',
                    'maxResults': 1
                }
                yt_res = requests.get(yt_url, params=params)
                yt_data = yt_res.json()
                
                if "items" in yt_data and len(yt_data["items"]) > 0:
                    video_id = yt_data["items"][0]["id"]["videoId"]
            except Exception as e:
                print(f"YouTube Search Failed: {e}")
                # Fallback: video_id remains None (Defensive Coding)
        
        # 3. Construct Final Response
        return LectureResponse(
            answer=ProfessorContent(
                definition=ai_data.get("definition", "Definition unavailable."),
                key_notes=ai_data.get("key_notes", []),
                application=ai_data.get("application", "N/A")
            ),
            video_id=video_id
        )

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
