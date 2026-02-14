from __future__ import annotations

import streamlit as st


def apply_classroom_styles() -> None:
    st.markdown(
        """
        <style>
        .hero {
            text-align: center;
            padding: 0.5rem 0 1.5rem 0;
        }
        .hero-icon {
            font-size: 3rem;
            display: inline-block;
            animation: floatUpDown 2.4s ease-in-out infinite;
        }
        .section-gap {
            margin-top: 0.75rem;
            margin-bottom: 0.75rem;
        }
        @keyframes floatUpDown {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
            100% { transform: translateY(0px); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(history: list[str]) -> str:
    with st.sidebar:
        st.markdown("## AI Professor")
        st.caption("Virtual AI Classroom")
        mode = st.radio("Learning mode", ["Beginner", "Advanced"], index=0)
        st.markdown("---")
        st.markdown("### Topic history")
        if history:
            for item in history[-10:][::-1]:
                st.caption(f"- {item}")
        else:
            st.caption("No history yet.")
        if st.button("Clear history", use_container_width=True):
            st.session_state.topic_history = []
            st.success("History cleared")
    return mode


def render_top_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-icon">&#127891;</div>
            <h1>AI Professor</h1>
            <h3>Your Virtual AI Learning Classroom</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown("---")
    st.caption("AI Professor | Learn with clarity, structure, and momentum.")