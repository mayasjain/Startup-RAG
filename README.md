# Startup Advisor — RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers startup questions using a curated knowledge base of essays and articles (Paul Graham, YC advice, fundraising guides, etc.). Built with Streamlit, FAISS, and the Groq API (Llama 3.3 70B).

---

## How It Works

```
User question
      │
      ▼
 Embedding model         ← sentence-transformers (all-MiniLM-L6-v2)
 encodes the query
      │
      ▼
 FAISS vector search     ← cosine similarity over pre-built index
 returns top-k chunks
      │
      ▼
 Groq LLM (Llama 3.3)   ← context-grounded answer, streamed
 generates an answer
      │
      ▼
  Streamlit UI
  (with sources shown)
```

Each answer is grounded in the retrieved document chunks. The UI shows an expandable **Sources** panel below every assistant reply so you can see exactly which document passages were used.

---

## Project Structure

```
.
├── app.py          # Streamlit UI — landing page + chat view
├── ingest.py       # Build the FAISS index from docs/
├── retrieval.py    # Query the FAISS index, return top-k chunks
├── llm.py          # Groq API wrapper (streaming + non-streaming)
├── scrape.py       # Scrape any URL and save it to docs/
├── docs/           # Knowledge base — plain .txt files
├── data/
│   ├── index.faiss     # Pre-built vector index (not committed if large)
│   └── metadata.pkl    # Chunk text + source metadata
└── requirements.txt
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd "Startup RAG"
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The first run downloads the `all-MiniLM-L6-v2` embedding model (~90 MB) automatically.

### 3. Set your Groq API key

Create a `.env` file (copy from the example):

```bash
cp .env.example .env
```

Then edit `.env`:

```
GROQ_API_KEY=your_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 4. Build the vector index

This only needs to be run once (or whenever you add/change documents in `docs/`):

```bash
python ingest.py
```

This reads every `.txt` file in `docs/`, chunks them into ~500-character overlapping segments, embeds them with `all-MiniLM-L6-v2`, and writes `data/index.faiss` + `data/metadata.pkl`.

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Adding Your Own Documents

### Option A — Paste a text file

Drop any `.txt` file into `docs/`, then rebuild the index:

```bash
python ingest.py
```

### Option B — Scrape a webpage

```bash
python scrape.py https://paulgraham.com/startupfunding.html
python ingest.py
```

You can pass multiple URLs at once:

```bash
python scrape.py https://example.com/article1 https://example.com/article2
python ingest.py
```

The scraper strips navigation, scripts, and boilerplate, then saves clean text to `docs/`.

---

## Deploying to Streamlit Cloud

1. Push your repo to GitHub (make sure `data/index.faiss` and `data/metadata.pkl` are committed).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. In **App settings → Secrets**, add:
   ```
   GROQ_API_KEY = "your_key_here"
   ```
   The app reads from `st.secrets` automatically when running on Streamlit Cloud.

---

## Architecture Details

| Component | Choice | Why |
|---|---|---|
| Embedding model | `all-MiniLM-L6-v2` | Fast, small (~90 MB), strong semantic search |
| Vector store | FAISS `IndexFlatIP` | Exact inner-product search; no server needed |
| Similarity metric | Cosine (via L2 normalization + dot product) | More robust than raw dot product |
| LLM | Llama 3.3 70B via Groq | Fast inference, free tier available |
| Chunking | Paragraph-aware, 500 chars, 50-char overlap | Preserves semantic boundaries |
| Source diversity | Max 2 chunks per source | Prevents one doc dominating the context |
| Retrieval threshold | 0.3 cosine score | Filters low-relevance chunks |
| History window | Last 6 messages | Keeps follow-up questions coherent |

---

## Tech Stack

- [Streamlit](https://streamlit.io) — UI
- [sentence-transformers](https://www.sbert.net) — embeddings
- [FAISS](https://github.com/facebookresearch/faiss) — vector search
- [Groq](https://groq.com) — LLM inference (Llama 3.3 70B)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — web scraping
