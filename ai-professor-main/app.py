from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv
from graphviz import Digraph

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import google.generativeai as genai
except Exception:
    genai = None


load_dotenv()

st.set_page_config(page_title="AI Professor", page_icon="\U0001F393", layout="wide")


@dataclass
class GenerationResult:
    simple_explanation: str
    real_world_applications: list[str]
    key_concepts: list[str]
    what_to_learn_next: list[str]
    mini_learning_roadmap: dict[str, list[str]]
    suggested_projects: list[str]
    interview_questions: list[str]
    prerequisites: list[str]
    next_logical_topic: str
    recommended_skills: list[str]
    mermaid_diagram: str


def init_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "video_data" not in st.session_state:
        st.session_state.video_data = None


@st.cache_resource
def get_llm_client(provider: str) -> Any:
    if provider == "OpenAI":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment.")
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        return OpenAI(api_key=api_key)

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in environment.")
    if genai is None:
        raise RuntimeError("google-generativeai package is not installed.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


@st.cache_data(ttl=3600, show_spinner=False)
def search_youtube_video(topic: str, api_key: str) -> dict[str, str] | None:
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": f"{topic} tutorial educational",
        "type": "video",
        "safeSearch": "strict",
        "key": api_key,
    }
    response = requests.get(url, params=params, timeout=20)
    data = response.json()

    if response.status_code != 200:
        error = data.get("error", {})
        message = error.get("message", "YouTube API request failed.")
        reason = ""
        if error.get("errors"):
            reason = error["errors"][0].get("reason", "")
        raise RuntimeError(f"YouTube API error: {reason or message}")

    items = data.get("items", [])
    if not items:
        return None

    item = items[0]
    video_id = item.get("id", {}).get("videoId")
    title = item.get("snippet", {}).get("title", "Untitled video")
    if not video_id:
        return None

    return {
        "video_id": video_id,
        "title": title,
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
    }


@st.cache_data(ttl=3600, show_spinner=False)
def generate_learning_content(topic: str, mode: str, provider: str) -> GenerationResult:
    schema = {
        "simple_explanation": "string",
        "real_world_applications": ["string"],
        "key_concepts": ["string"],
        "what_to_learn_next": ["string"],
        "mini_learning_roadmap": {
            "Beginner": ["string"],
            "Intermediate": ["string"],
            "Advanced": ["string"],
        },
        "suggested_projects": ["string"],
        "interview_questions": ["string"],
        "prerequisites": ["string"],
        "next_logical_topic": "string",
        "recommended_skills": ["string"],
        "mermaid_diagram": "string",
    }

    prompt = f"""
You are AI Professor, an expert educator.
Audience mode: {mode}.
Topic: {topic}

Return ONLY valid JSON matching this schema:
{json.dumps(schema)}

Rules:
- Keep simple_explanation concise and clear.
- Provide 4-6 items for lists where meaningful.
- Make prerequisites and next topic non-generic and topic-specific.
- Mermaid diagram must be valid flowchart syntax starting with: flowchart TD
- No markdown fences. No extra keys.
""".strip()

    client = get_llm_client(provider)

    if provider == "OpenAI":
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.3,
            max_output_tokens=1200,
        )
        text = response.output_text
    else:
        response = client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "response_mime_type": "application/json",
            },
        )
        text = response.text

    payload = safe_json_parse(text)
    return GenerationResult(
        simple_explanation=payload.get("simple_explanation", "Explanation unavailable."),
        real_world_applications=normalize_list(payload.get("real_world_applications")),
        key_concepts=normalize_list(payload.get("key_concepts")),
        what_to_learn_next=normalize_list(payload.get("what_to_learn_next")),
        mini_learning_roadmap=normalize_roadmap(payload.get("mini_learning_roadmap")),
        suggested_projects=normalize_list(payload.get("suggested_projects")),
        interview_questions=normalize_list(payload.get("interview_questions")),
        prerequisites=normalize_list(payload.get("prerequisites")),
        next_logical_topic=str(payload.get("next_logical_topic", "Not available")),
        recommended_skills=normalize_list(payload.get("recommended_skills")),
        mermaid_diagram=str(payload.get("mermaid_diagram", "")),
    )


def safe_json_parse(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise RuntimeError("Model did not return valid JSON.")


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_roadmap(value: Any) -> dict[str, list[str]]:
    default = {"Beginner": [], "Intermediate": [], "Advanced": []}
    if not isinstance(value, dict):
        return default
    for key in default:
        default[key] = normalize_list(value.get(key))
    return default


def render_bullets(items: list[str], empty_text: str = "No data available.") -> None:
    if not items:
        st.write(empty_text)
        return
    for item in items:
        st.markdown(f"- {item}")


def render_graphviz_fallback(key_concepts: list[str]) -> None:
    if not key_concepts:
        st.info("No diagram data available.")
        return

    dot = Digraph()
    dot.attr(rankdir="LR")
    dot.node("topic", "Core Topic")
    for idx, concept in enumerate(key_concepts[:6]):
        node_id = f"c{idx}"
        dot.node(node_id, concept)
        dot.edge("topic", node_id)
    st.graphviz_chart(dot)


def render_header() -> None:
    st.title("AI Professor")
    st.markdown("### Your structured AI learning workspace")
    st.caption("From first principles to projects, interviews, and guided next steps.")


def render_sidebar() -> tuple[str, str, str]:
    with st.sidebar:
        st.markdown("## AI Professor")
        st.caption("Learn faster with structured explanations, video, diagrams, and roadmaps.")

        mode = st.radio("Learning Mode", ["Beginner", "Advanced"], index=0)
        provider = st.selectbox("LLM Provider", ["Gemini", "OpenAI"])
        topic = st.text_input("Topic", placeholder="e.g., Retrieval-Augmented Generation")

        st.markdown("---")
        st.markdown("### Topic History")
        if st.session_state.history:
            for item in st.session_state.history[-8:][::-1]:
                st.caption(f"- {item}")
        else:
            st.caption("No topics yet.")

        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.success("History cleared.")

    return topic.strip(), mode, provider


def run_generation(topic: str, mode: str, provider: str) -> None:
    if not topic:
        st.error("Please enter a topic before generating content.")
        return

    with st.spinner("Generating explanation and roadmap..."):
        try:
            result = generate_learning_content(topic, mode, provider)
            st.session_state.last_result = result
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
        except Exception as exc:
            message = str(exc)
            lowered = message.lower()
            if "rate" in lowered or "quota" in lowered or "429" in lowered:
                st.error("LLM rate limit exceeded. Please retry in a minute.")
            else:
                st.error(f"Content generation failed: {exc}")
            return

    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    video_data = None
    if youtube_api_key:
        with st.spinner("Finding a relevant video..."):
            try:
                video_data = search_youtube_video(topic, youtube_api_key)
            except Exception as exc:
                message = str(exc).lower()
                if "quota" in message or "ratelimit" in message or "403" in message:
                    st.warning("YouTube API quota exceeded. Please try again later.")
                else:
                    st.warning(f"Video lookup failed: {exc}")
    else:
        st.info("YOUTUBE_API_KEY not configured. Skipping video search.")

    st.session_state.video_data = video_data


def render_tabs(result: GenerationResult) -> None:
    tabs = st.tabs([
        "\U0001F4D8 Explanation",
        "\U0001F3A5 Video",
        "\U0001F4CA Diagram",
        "\U0001F6E3 Roadmap",
    ])

    with tabs[0]:
        with st.container(border=True):
            st.subheader("SECTION 1: Simple Explanation")
            st.write(result.simple_explanation)
        with st.container(border=True):
            st.subheader("SECTION 2: Real-World Applications")
            render_bullets(result.real_world_applications)
        with st.container(border=True):
            st.subheader("SECTION 3: Key Concepts")
            render_bullets(result.key_concepts)

    with tabs[1]:
        st.subheader("Relevant YouTube Lesson")
        video_data = st.session_state.get("video_data")
        if video_data and video_data.get("embed_url"):
            st.video(video_data["embed_url"])
            st.caption(video_data.get("title", ""))
        else:
            st.warning("No suitable video found for this topic.")

    with tabs[2]:
        with st.container(border=True):
            st.subheader("SECTION 4: Diagram")
            diagram_text = result.mermaid_diagram.strip()
            if diagram_text.lower().startswith("flowchart"):
                st.markdown("Mermaid diagram source")
                st.code(diagram_text, language="mermaid")
                st.caption("Graphviz fallback view:")
                render_graphviz_fallback(result.key_concepts)
            else:
                st.info("Diagram generation returned invalid syntax. Showing fallback.")
                render_graphviz_fallback(result.key_concepts)

    with tabs[3]:
        with st.container(border=True):
            st.subheader("SECTION 5: What To Learn Next")
            render_bullets(result.what_to_learn_next)

        with st.container(border=True):
            st.subheader("SECTION 6: Mini Learning Roadmap (Beginner -> Intermediate -> Advanced)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Beginner**")
                render_bullets(result.mini_learning_roadmap.get("Beginner", []))
            with c2:
                st.markdown("**Intermediate**")
                render_bullets(result.mini_learning_roadmap.get("Intermediate", []))
            with c3:
                st.markdown("**Advanced**")
                render_bullets(result.mini_learning_roadmap.get("Advanced", []))

        with st.container(border=True):
            st.subheader("Learning Guidance Engine")
            left, right = st.columns(2)
            with left:
                st.markdown("**Prerequisites**")
                render_bullets(result.prerequisites)
            with right:
                st.markdown("**Recommended Skills**")
                render_bullets(result.recommended_skills)
            st.markdown(f"**Next Logical Topic:** {result.next_logical_topic}")

        with st.container(border=True):
            st.subheader("SECTION 7: Suggested Projects")
            render_bullets(result.suggested_projects)

        with st.container(border=True):
            st.subheader("SECTION 8: Interview Questions")
            render_bullets(result.interview_questions)


def render_footer() -> None:
    st.markdown("---")
    st.caption("AI Professor | Build mastery with structured learning paths and practical projects.")


def main() -> None:
    init_state()
    render_header()

    topic, mode, provider = render_sidebar()
    if st.button("Generate Learning Pack", type="primary", use_container_width=True):
        run_generation(topic, mode, provider)

    result = st.session_state.get("last_result")
    if not result:
        st.info("Enter a topic and generate your learning pack.")
        render_footer()
        return

    render_tabs(result)
    render_footer()


if __name__ == "__main__":
    main()

