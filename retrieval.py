import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = "data"
MODEL_NAME = "all-MiniLM-L6-v2"

_index = None
_metadata = None
_model = None


def _load():
    global _index, _metadata, _model
    if _index is None:
        _index = faiss.read_index(f"{DATA_DIR}/index.faiss")
        with open(f"{DATA_DIR}/metadata.pkl", "rb") as f:
            _metadata = pickle.load(f)
        _model = SentenceTransformer(MODEL_NAME)


def retrieve(query, k=4):
    _load()
    embedding = _model.encode([query], convert_to_numpy=True).astype(np.float32)
    distances, indices = _index.search(embedding, k)
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1:
            continue
        chunk = _metadata[idx].copy()
        chunk["score"] = float(dist)
        results.append(chunk)
    return results


if __name__ == "__main__":
    query = input("Enter a test query: ")
    chunks = retrieve(query)
    print(f"\nTop {len(chunks)} chunks:\n")
    for i, c in enumerate(chunks, 1):
        print(f"[{i}] Source: {c['source']} | Score: {c['score']:.4f}")
        print(c["text"][:300])
        print()
