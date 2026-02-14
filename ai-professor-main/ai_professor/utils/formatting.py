from __future__ import annotations

from graphviz import Digraph
import streamlit as st


def render_bullets(items: list[str], empty_message: str = "No data available.") -> None:
    if not items:
        st.write(empty_message)
        return
    for item in items:
        st.markdown(f"- {item}")


def render_diagram(mermaid_text: str, key_concepts: list[str]) -> None:
    cleaned = (mermaid_text or "").strip()
    if cleaned.lower().startswith("flowchart"):
        st.markdown("Mermaid source")
        st.code(cleaned, language="mermaid")

    st.markdown("Graphviz diagram")
    dot = Digraph()
    dot.attr(rankdir="LR")
    dot.node("topic", "Core Topic")

    concepts = key_concepts[:8] if key_concepts else ["No concepts generated"]
    for index, concept in enumerate(concepts):
        node = f"k{index}"
        dot.node(node, concept)
        dot.edge("topic", node)

    st.graphviz_chart(dot)