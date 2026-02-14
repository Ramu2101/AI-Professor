from __future__ import annotations

from graphviz import Digraph
import streamlit as st


def render_concept_diagram(topic: str, key_concepts: list[str], applications: list[str]) -> None:
    try:
        graph = Digraph()
        graph.attr(rankdir="LR")

        topic_id = "topic"
        graph.node(topic_id, topic)

        concept_nodes: list[str] = []
        for index, concept in enumerate(key_concepts[:8]):
            node_id = f"concept_{index}"
            graph.node(node_id, concept)
            graph.edge(topic_id, node_id)
            concept_nodes.append(node_id)

        for index, app in enumerate(applications[:6]):
            app_id = f"app_{index}"
            graph.node(app_id, app)
            if concept_nodes:
                graph.edge(concept_nodes[index % len(concept_nodes)], app_id)
            else:
                graph.edge(topic_id, app_id)

        st.graphviz_chart(graph, use_container_width=True)
    except Exception:
        st.warning("Diagram rendering failed. Showing structured fallback.")
        st.markdown(f"- **Topic:** {topic}")
        for concept in key_concepts:
            st.markdown(f"  - **Concept:** {concept}")
        for app in applications:
            st.markdown(f"  - **Application:** {app}")