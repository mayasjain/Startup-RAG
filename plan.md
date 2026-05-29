# Startup RAG Chatbot

A web chatbot answering startup questions from a local document knowledge base using RAG.

## Stack
- Embeddings: sentence-transformers `all-MiniLM-L6-v2` (local, free)
- Vector store: FAISS
- LLM: Groq `llama-3.1-8b-instant`
- UI: Streamlit
- Deploy: Streamlit Cloud (free, public URL)

## File Structure
```
docs/           # .txt startup articles/blog posts
data/           # generated FAISS index + metadata
ingest.py       # chunk → embed → save to FAISS
retrieval.py    # embed query → top-k chunks
llm.py          # Groq call with retrieved context
app.py          # Streamlit chat UI
.env            # GROQ_API_KEY
```

## Phases
1. **Local pipeline** — ingest.py chunks .txt docs, embeds, saves FAISS index
2. **LLM** — llm.py retrieves chunks + calls Groq, test in terminal
3. **UI** — app.py Streamlit chat with sources panel
4. **Real docs** — add actual startup content, re-run ingestion
5. **Deploy** — push to GitHub, deploy on Streamlit Cloud

## Mode
Single-shot Q&A (no conversation memory). Sources shown per answer.
