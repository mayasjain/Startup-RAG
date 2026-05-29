import re
import streamlit as st
from retrieval import retrieve
from llm import answer, answer_stream


def display_name(filename):
    name = filename.removesuffix(".txt")
    # scraped files: "paulgraham_com_slug_html" → "slug"
    name = re.sub(r"^[a-z0-9]+_com_(.+?)(?:_html)?$", r"\1", name)
    return name.replace("_", " ").title()

st.title("Startup Advisor")
st.caption("Ask anything about fundraising, product-market fit, hiring, and more.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources"):
                for chunk in msg["sources"]:
                    st.markdown(f"**{display_name(chunk['source'])}**")
                    st.caption(chunk["text"][:300] + "...")

if question := st.chat_input("Ask a startup question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Finding relevant sources..."):
            chunks = retrieve(question, k=4)
        history = st.session_state.messages[:-1][-6:]
        response = st.write_stream(answer_stream(question, chunks, history))
        with st.expander("Sources"):
            for chunk in chunks:
                st.markdown(f"**{display_name(chunk['source'])}**")
                st.caption(chunk["text"][:300] + "...")

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": chunks,
    })
