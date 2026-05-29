import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DOCS_DIR = "docs"
DATA_DIR = "data"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MODEL_NAME = "all-MiniLM-L6-v2"


def load_documents(docs_dir):
    docs = []
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            path = os.path.join(docs_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                docs.append({"filename": filename, "text": f.read()})
    return docs


def chunk_text(text, chunk_size, overlap):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_parts = []
    current_len = 0

    for para in paragraphs:
        if len(para) > chunk_size:
            if current_parts:
                chunks.append("\n\n".join(current_parts))
                current_parts, current_len = [], 0
            start = 0
            while start < len(para):
                chunks.append(para[start:start + chunk_size])
                start += chunk_size - overlap
            continue

        if current_len + len(para) > chunk_size and current_parts:
            chunks.append("\n\n".join(current_parts))
            current_parts = current_parts[-1:]
            current_len = len(current_parts[0])

        current_parts.append(para)
        current_len += len(para)

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def build_chunks(docs):
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"], CHUNK_SIZE, CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk.strip(),
                "source": doc["filename"],
                "chunk_id": i,
            })
    return all_chunks


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Loading documents...")
    docs = load_documents(DOCS_DIR)
    print(f"  {len(docs)} documents loaded")

    print("Chunking...")
    chunks = build_chunks(docs)
    print(f"  {len(chunks)} chunks created")

    print("Embedding (first run downloads the model ~90MB)...")
    model = SentenceTransformer(MODEL_NAME)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    print("Building FAISS index...")
    dim = embeddings.shape[1]
    embeddings = embeddings.astype(np.float32)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(DATA_DIR, "index.faiss"))
    with open(os.path.join(DATA_DIR, "metadata.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"Done. Saved {len(chunks)} chunks to data/")


if __name__ == "__main__":
    main()
