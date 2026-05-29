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


def retrieve(query, k=4, threshold=0.3, max_per_source=2):
    _load()
    embedding = _model.encode([query], convert_to_numpy=True).astype(np.float32)
    faiss.normalize_L2(embedding)
    distances, indices = _index.search(embedding, k * 3)
    results = []
    source_counts = {}
    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1 or dist < threshold:
            continue
        chunk = _metadata[idx].copy()
        source = chunk["source"]
        if source_counts.get(source, 0) >= max_per_source:
            continue
        chunk["score"] = float(dist)
        results.append(chunk)
        source_counts[source] = source_counts.get(source, 0) + 1
        if len(results) == k:
            break
    return results


if __name__ == "__main__":
    query = input("Enter a test query: ")
    chunks = retrieve(query)
    print(f"\nTop {len(chunks)} chunks:\n")
    for i, c in enumerate(chunks, 1):
        print(f"[{i}] Source: {c['source']} | Score: {c['score']:.4f}")
        print(c["text"][:300])
        print()
