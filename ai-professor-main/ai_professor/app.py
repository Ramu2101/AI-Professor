from __future__ import annotations

import streamlit as st

from ai_professor.components.diagram import render_concept_diagram
from ai_professor.components.layout import (
    apply_classroom_styles,
    render_footer,
    render_sidebar,
    render_top_header,
)
from urllib.parse import quote_plus

from ai_professor.services.gemini_service import GeminiServiceError, LearningContent, generate_learning_content
from ai_professor.services.youtube_service import YouTubeServiceError, search_youtube_video


st.set_page_config(page_title="AI Professor", page_icon="\U0001F393", layout="wide")


def _init_state() -> None:
    if "topic_history" not in st.session_state:
        st.session_state.topic_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_video" not in st.session_state:
        st.session_state.last_video = None


def _render_bullets(items: list[str], empty_text: str = "No items available.") -> None:
    if not items:
        st.write(empty_text)
        return
    for item in items:
        st.markdown(f"- {item}")


def _generate(topic: str, mode: str, youtube_api_key: str | None) -> None:
    if not topic:
        st.error("Please enter a topic before generating content.")
        return

    with st.spinner("Professor is thinking..."):
        try:
            content = generate_learning_content(topic=topic, mode=mode)
        except GeminiServiceError as exc:
            st.error(str(exc))
            if "quota" in str(exc).lower() or "resourceexhausted" in str(exc).lower() or "429" in str(exc):
                st.info("This is a Gemini project/key quota limit. Use a different API key, wait for quota reset, or enable billing in Google AI Studio/Cloud.")
            return
        except Exception as exc:
            st.error(f"Unexpected error while generating content: {exc}")
            return

    video: dict | None = None
    if youtube_api_key:
        with st.spinner("Professor is finding a lesson video..."):
            try:
                video = search_youtube_video(topic=topic, youtube_api_key=youtube_api_key)
            except YouTubeServiceError as exc:
                st.warning(str(exc))
            except Exception:
                st.warning("Unable to fetch YouTube video right now.")
    else:
        search_query = quote_plus(f"{topic} tutorial")
        video = {
            "title": f"{topic} tutorial (YouTube search)",
            "search_url": f"https://www.youtube.com/results?search_query={search_query}",
        }

    if video is None:
        search_query = quote_plus(f"{topic} tutorial")
        video = {
            "title": f"{topic} tutorial (YouTube search)",
            "search_url": f"https://www.youtube.com/results?search_query={search_query}",
        }

    st.session_state.last_result = content
    st.session_state.last_video = video
    if topic not in st.session_state.topic_history:
        st.session_state.topic_history.append(topic)


def _render_results(topic: str, content: LearningContent, video: dict | None) -> None:
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
            st.write(content.simple_explanation)

        with st.container(border=True):
            st.subheader("SECTION 2: Key Concepts")
            _render_bullets(content.key_concepts)

        with st.container(border=True):
            st.subheader("SECTION 3: Real-world Applications")
            _render_bullets(content.real_world_applications)

    with tabs[1]:
        with st.container(border=True):
            st.subheader("Video Lesson")
            if video and video.get("url"):
                st.video(video["url"])
                if video.get("title"):
                    st.caption(video["title"])
            elif video and video.get("search_url"):
                st.link_button("Open YouTube results", video["search_url"], use_container_width=True)
                if video.get("title"):
                    st.caption(video["title"])
            else:
                st.info("No video found for this topic.")

    with tabs[2]:
        with st.container(border=True):
            st.subheader("SECTION 4: Diagram")
            render_concept_diagram(topic, content.key_concepts, content.real_world_applications)

    with tabs[3]:
        with st.container(border=True):
            st.subheader("SECTION 5: Prerequisites")
            _render_bullets(content.prerequisites)

        with st.container(border=True):
            st.subheader("SECTION 6: What To Learn Next")
            _render_bullets(content.what_to_learn_next)

        with st.container(border=True):
            st.subheader("SECTION 7: Roadmap (Beginner -> Intermediate -> Advanced)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Beginner**")
                _render_bullets(content.roadmap.get("Beginner", []))
            with c2:
                st.markdown("**Intermediate**")
                _render_bullets(content.roadmap.get("Intermediate", []))
            with c3:
                st.markdown("**Advanced**")
                _render_bullets(content.roadmap.get("Advanced", []))

    with tabs[4]:
        with st.container(border=True):
            st.subheader("SECTION 8: Suggested Projects")
            _render_bullets(content.suggested_projects)

        with st.container(border=True):
            st.subheader("SECTION 9: Interview Questions")
            _render_bullets(content.interview_questions)


def main() -> None:
    _init_state()
    apply_classroom_styles()

    mode = render_sidebar(st.session_state.topic_history)
    render_top_header()

    if "GEMINI_API_KEY" not in st.secrets:
        st.error("GEMINI_API_KEY missing. Add it to Streamlit Secrets.")
        st.stop()

    youtube_api_key = st.secrets["YOUTUBE_API_KEY"] if "YOUTUBE_API_KEY" in st.secrets else None

    _, center, _ = st.columns([1, 5, 1])
    with center:
        topic = st.text_input("Enter topic", placeholder="e.g., Attention Mechanism in Transformers")
        generate_clicked = st.button("Generate Classroom Session", type="primary", use_container_width=True)

    if generate_clicked:
        _generate(topic=topic.strip(), mode=mode, youtube_api_key=youtube_api_key)

    if st.session_state.last_result:
        current_topic = topic.strip() if topic.strip() else st.session_state.topic_history[-1]
        _render_results(current_topic, st.session_state.last_result, st.session_state.last_video)
    else:
        st.info("Enter a topic and generate your learning session.")

    render_footer()


if __name__ == "__main__":
    main()
