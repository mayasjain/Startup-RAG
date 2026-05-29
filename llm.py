import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        try:
            import streamlit as st
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = os.environ["GROQ_API_KEY"]
        _client = Groq(api_key=api_key)
    return _client


def _messages(question, chunks, history=None):
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )
    msgs = [
        {
            "role": "system",
            "content": (
                "You are a startup advisor. Answer the user's question using only "
                "the context provided below. Be concise and specific. "
                "At the end of your answer, note which source(s) you drew from.\n\n"
                f"Context:\n{context}"
            ),
        }
    ]
    for msg in (history or []):
        msgs.append({"role": msg["role"], "content": msg["content"]})
    msgs.append({"role": "user", "content": question})
    return msgs


def answer(question, chunks, history=None):
    response = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=_messages(question, chunks, history),
        temperature=0.3,
    )
    return response.choices[0].message.content


def answer_stream(question, chunks, history=None):
    stream = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=_messages(question, chunks, history),
        temperature=0.3,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


if __name__ == "__main__":
    from retrieval import retrieve
    question = input("Ask a startup question: ")
    chunks = retrieve(question, k=4)
    print("\nThinking...\n")
    print(answer(question, chunks))
