from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import google.generativeai as genai
import streamlit as st


class GeminiConfigError(RuntimeError):
    """Raised when Gemini configuration is invalid."""


class GeminiServiceError(RuntimeError):
    """Raised when Gemini request fails."""


@dataclass
class GeminiResponse:
    simple_explanation: str
    key_concepts: list[str]
    real_world_applications: list[str]
    diagram_mermaid: str
    prerequisites: list[str]
    what_to_learn_next: list[str]
    mini_roadmap: dict[str, list[str]]
    suggested_projects: list[str]
    interview_questions: list[str]


@st.cache_data(ttl=3600, show_spinner=False)
def generate_topic_pack(topic: str, mode: str, gemini_api_key: str) -> GeminiResponse:
    if not gemini_api_key:
        raise GeminiConfigError("GEMINI_API_KEY missing in environment.")

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as exc:
        raise GeminiConfigError(f"Gemini initialization failed: {exc}") from exc

    schema = {
        "simple_explanation": "string",
        "key_concepts": ["string"],
        "real_world_applications": ["string"],
        "diagram_mermaid": "flowchart TD\nA-->B",
        "prerequisites": ["string"],
        "what_to_learn_next": ["string"],
        "mini_roadmap": {
            "Beginner": ["string"],
            "Intermediate": ["string"],
            "Advanced": ["string"],
        },
        "suggested_projects": ["string"],
        "interview_questions": ["string"],
    }

    prompt = f"""
You are AI Professor, a structured technical educator.
User topic: {topic}
Audience mode: {mode}

Return JSON only with this schema:
{json.dumps(schema)}

Rules:
- Keep simple explanation clear and compact.
- Make outputs specific to the topic.
- Keep key concepts and prerequisites practical.
- diagram_mermaid must start with: flowchart TD
- No markdown fences. No extra keys.
""".strip()

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "response_mime_type": "application/json",
            },
        )
    except Exception as exc:
        message = str(exc).lower()
        if "quota" in message or "429" in message or "rate" in message:
            raise GeminiServiceError("Gemini API quota exceeded. Please try again later.") from exc
        if "api key" in message or "permission" in message or "unauthorized" in message:
            raise GeminiServiceError("Invalid Gemini API key or permission denied.") from exc
        if "network" in message or "connection" in message or "timeout" in message:
            raise GeminiServiceError("Network error while contacting Gemini API.") from exc
        raise GeminiServiceError(f"Gemini API request failed: {exc}") from exc

    payload = _safe_json_parse(getattr(response, "text", ""))

    return GeminiResponse(
        simple_explanation=str(payload.get("simple_explanation", "Explanation unavailable.")),
        key_concepts=_normalize_list(payload.get("key_concepts")),
        real_world_applications=_normalize_list(payload.get("real_world_applications")),
        diagram_mermaid=str(payload.get("diagram_mermaid", "")),
        prerequisites=_normalize_list(payload.get("prerequisites")),
        what_to_learn_next=_normalize_list(payload.get("what_to_learn_next")),
        mini_roadmap=_normalize_roadmap(payload.get("mini_roadmap")),
        suggested_projects=_normalize_list(payload.get("suggested_projects")),
        interview_questions=_normalize_list(payload.get("interview_questions")),
    )


def _safe_json_parse(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise GeminiServiceError("Gemini returned invalid JSON format.")


def _normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_roadmap(value: Any) -> dict[str, list[str]]:
    roadmap = {"Beginner": [], "Intermediate": [], "Advanced": []}
    if not isinstance(value, dict):
        return roadmap

    for level in roadmap:
        roadmap[level] = _normalize_list(value.get(level))
    return roadmap