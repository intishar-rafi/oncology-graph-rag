"""Streamlit frontend for the Oncology GraphRAG system."""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Oncology GraphRAG", page_icon="🧬", layout="wide")

page = st.sidebar.radio("Navigate", ["💬 Chat", "🔍 Explore", "📊 Graph Stats"])

st.sidebar.markdown("---")
st.sidebar.caption(
    "GraphRAG system over a Neo4j oncology knowledge graph "
    "(drugs, genes, cancer types, symptoms, trials). "
    "Educational/demo tool — not medical advice."
)

# ---------------------------------------------------------------------------
# CHAT PAGE
# ---------------------------------------------------------------------------
if page == "💬 Chat":
    st.title("🧬 Oncology GraphRAG Chat")
    st.write("Ask a question about cancer drugs, genes, diseases, or clinical trials.")

    examples = [
        "What drugs treat HER2-positive breast cancer and what gene do they target?",
        "Which drugs target EGFR and what cancers are they used for?",
        "What clinical trials tested pembrolizumab?",
        "Which genes are associated with both breast cancer and ovarian cancer?",
        "What symptoms are associated with pancreatic ductal adenocarcinoma?",
    ]
    st.caption("Try: " + " · ".join(f"*{e}*" for e in examples[:2]))

    if "history" not in st.session_state:
        st.session_state.history = []

    question = st.chat_input("Ask about oncology drugs, genes, diseases, or trials...")

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question:
        st.session_state.history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching the graph and generating an answer..."):
                try:
                    resp = requests.post(f"{API_URL}/ask", json={"question": question, "top_k": 3, "hops": 2})
                    resp.raise_for_status()
                    data = resp.json()
                    st.markdown(data["answer"])
                    with st.expander("Graph context used"):
                        for triple in data["graph_context"]:
                            st.code(triple, language="text")
                    st.session_state.history.append({"role": "assistant", "content": data["answer"]})
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------------------------------------------------------------------
# EXPLORE PAGE
# ---------------------------------------------------------------------------
elif page == "🔍 Explore":
    st.title("🔍 Explore the Knowledge Graph")

    col1, col2 = st.columns([1, 3])
    with col1:
        label = st.selectbox("Entity type", ["Disease", "Drug", "Gene", "Symptom", "Trial"])
    with col2:
        entity = st.text_input("Entity name", placeholder="e.g. HER2-positive breast cancer")

    hops = st.slider("Hops", 1, 3, 2)

    if entity:
        try:
            resp = requests.get(f"{API_URL}/graph/{entity}", params={"label": label, "hops": hops})
            if resp.status_code == 404:
                st.warning(f"No entity named '{entity}' found with type {label}.")
            else:
                resp.raise_for_status()
                rows = resp.json()
                st.write(f"**{len(rows)}** connected facts found:")
                for r in rows:
                    st.markdown(
                        f"`{r['source_label']}:{r['source']}` "
                        f"—[{r['relationship']}]→ "
                        f"`{r['target_label']}:{r['target']}`"
                    )
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")
    st.subheader("Drug / Disease profile lookup")
    profile_type = st.radio("Profile type", ["Drug", "Disease"], horizontal=True)
    profile_name = st.text_input("Name", key="profile_name", placeholder="e.g. Trastuzumab or Melanoma")
    if profile_name:
        endpoint = "drug" if profile_type == "Drug" else "disease"
        try:
            resp = requests.get(f"{API_URL}/{endpoint}/{profile_name}/profile")
            if resp.status_code == 404:
                st.warning(resp.json().get("detail", "Not found"))
            else:
                resp.raise_for_status()
                st.json(resp.json())
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------------------------------------------------------------------
# STATS PAGE
# ---------------------------------------------------------------------------
elif page == "📊 Graph Stats":
    st.title("📊 Graph Statistics")
    try:
        resp = requests.get(f"{API_URL}/stats")
        resp.raise_for_status()
        data = resp.json()

        st.subheader("Node counts")
        st.json(data["nodes"])

        st.subheader("Relationship counts")
        for rel in data["relationships"]:
            st.write(f"**{rel['relationship']}**: {rel['count']}")
    except Exception as e:
        st.error(f"Error: {e}")
