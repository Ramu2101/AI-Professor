from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from ai_professor.services.gemini_service import (
    GeminiConfigError,
    GeminiResponse,
    GeminiServiceError,
    generate_topic_pack,
)
from ai_professor.services.youtube_service import (
    YouTubeServiceError,
    search_youtube_video,
)
from ai_professor.utils.formatting import render_bullets, render_diagram


load_dotenv()


st.set_page_config(
    page_title="AI Professor",
    page_icon="\U0001F393",
    layout="wide",
)


def _safe_secret(name: str) -> str | None:
    value = None
    try:
        if name in st.secrets:
            value = st.secrets[name]
    except Exception:
        value = None

    if isinstance(value, str) and value.strip():
        return value.strip()

    env_value = os.getenv(name)
    if isinstance(env_value, str) and env_value.strip():
        return env_value.strip()

    return None


def _init_state() -> None:
    if "topic_history" not in st.session_state:
        st.session_state.topic_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_video" not in st.session_state:
        st.session_state.last_video = None


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## AI Professor")
        st.caption("Structured AI Learning System")
        st.markdown("---")
        st.markdown("### Topic History")
        history = st.session_state.topic_history
        if history:
            for topic in history[-10:][::-1]:
                st.caption(f"- {topic}")
        else:
            st.caption("No topics generated yet.")

        if st.button("Clear history", use_container_width=True):
            st.session_state.topic_history = []
            st.success("History cleared")


def _render_header() -> None:
    st.title("AI Professor")
    st.markdown("### Your structured AI learning workspace")
    st.write("")


def _render_main_controls() -> tuple[str, str, bool]:
    _, center, _ = st.columns([1, 4, 1])
    with center:
        topic = st.text_input(
            "Enter a topic",
            placeholder="e.g., Transformer Architecture in NLP",
            label_visibility="visible",
        )
        mode = st.radio(
            "Learning mode",
            ["Beginner", "Advanced"],
            horizontal=True,
        )
        generate_clicked = st.button(
            "Generate Learning Pack",
            type="primary",
            use_container_width=True,
        )
    return topic.strip(), mode, generate_clicked


def _debug_key_status(gemini_key: str | None, youtube_key: str | None) -> None:
    gemini_ok = "available" if gemini_key else "missing"
    youtube_ok = "available" if youtube_key else "missing"
    st.caption(f"Environment check: GEMINI_API_KEY={gemini_ok}, YOUTUBE_API_KEY={youtube_ok}")


def _run_generation(topic: str, mode: str, gemini_key: str, youtube_key: str | None) -> None:
    if not topic:
        st.error("Please enter a topic before generating content.")
        return

    with st.spinner("Generating structured learning content..."):
        try:
            result = generate_topic_pack(topic=topic, mode=mode, gemini_api_key=gemini_key)
        except GeminiConfigError as exc:
            st.error(str(exc))
            return
        except GeminiServiceError as exc:
            st.error(str(exc))
            return
        except Exception:
            st.error("Unexpected error while generating content. Please try again.")
            return

    video = None
    if youtube_key:
        with st.spinner("Searching YouTube lesson..."):
            try:
                video = search_youtube_video(topic=topic, youtube_api_key=youtube_key)
            except YouTubeServiceError as exc:
                st.warning(str(exc))
            except Exception:
                st.warning("Unable to fetch YouTube video due to an unexpected error.")

    st.session_state.last_result = result
    st.session_state.last_video = video
    if topic not in st.session_state.topic_history:
        st.session_state.topic_history.append(topic)


def _render_results(result: GeminiResponse, video: dict[str, Any] | None) -> None:
    tabs = st.tabs([
        "\U0001F4D8 Explanation",
        "\U0001F3A5 Video",
        "\U0001F4CA Diagram",
        "\U0001F6E3 Roadmap",
        "\U0001F4A1 Projects & Interview",
    ])

    with tabs[0]:
        with st.container(border=True):
            st.subheader("SECTION 1: Simple Explanation")
            st.write(result.simple_explanation)

        with st.container(border=True):
            st.subheader("SECTION 2: Key Concepts")
            render_bullets(result.key_concepts)

        with st.container(border=True):
            st.subheader("SECTION 3: Real World Applications")
            render_bullets(result.real_world_applications)

    with tabs[1]:
        with st.container(border=True):
            st.subheader("Relevant Video")
            if video and video.get("video_url"):
                st.video(video["video_url"])
                if video.get("title"):
                    st.caption(video["title"])
            else:
                st.info("No relevant video found for this topic.")

    with tabs[2]:
        with st.container(border=True):
            st.subheader("SECTION 4: Diagram")
            render_diagram(result.diagram_mermaid, result.key_concepts)

    with tabs[3]:
        with st.container(border=True):
            st.subheader("SECTION 5: Prerequisites")
            render_bullets(result.prerequisites)

        with st.container(border=True):
            st.subheader("SECTION 6: What To Learn Next")
            render_bullets(result.what_to_learn_next)

        with st.container(border=True):
            st.subheader("SECTION 7: Mini Roadmap (Beginner -> Advanced)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Beginner**")
                render_bullets(result.mini_roadmap.get("Beginner", []))
            with c2:
                st.markdown("**Intermediate**")
                render_bullets(result.mini_roadmap.get("Intermediate", []))
            with c3:
                st.markdown("**Advanced**")
                render_bullets(result.mini_roadmap.get("Advanced", []))

    with tabs[4]:
        with st.container(border=True):
            st.subheader("SECTION 8: Suggested Projects")
            render_bullets(result.suggested_projects)

        with st.container(border=True):
            st.subheader("SECTION 9: Interview Questions")
            render_bullets(result.interview_questions)


def _render_footer() -> None:
    st.markdown("---")
    st.caption("AI Professor | Structured AI Learning System")


def main() -> None:
    _init_state()

    gemini_key = _safe_secret("GEMINI_API_KEY") or _safe_secret("GOOGLE_API_KEY")
    youtube_key = _safe_secret("YOUTUBE_API_KEY")

    _render_sidebar()
    _render_header()
    _debug_key_status(gemini_key, youtube_key)

    if not gemini_key:
        st.error("GEMINI_API_KEY missing in environment.")
        st.stop()

    topic, mode, generate_clicked = _render_main_controls()
    if generate_clicked:
        _run_generation(topic=topic, mode=mode, gemini_key=gemini_key, youtube_key=youtube_key)

    result = st.session_state.last_result
    if result:
        _render_results(result, st.session_state.last_video)
    else:
        st.info("Enter a topic and click Generate Learning Pack.")

    _render_footer()


if __name__ == "__main__":
    main()