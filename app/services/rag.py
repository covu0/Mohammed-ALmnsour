import os
import glob
import re
from typing import List, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except Exception:
    faiss = None

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
KB_DIR = os.getenv("KB_DIR", "kb")

_model = None  # lazy sentence-transformers model or None
_index = None
_chunks: List[str] = []
_meta: List[str] = []
_embeddings: np.ndarray | None = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _model = SentenceTransformer(MODEL_NAME)
    except Exception:
        _model = None
    return _model


def _read_kb_files() -> List[Tuple[str, str]]:
    files = glob.glob(os.path.join(KB_DIR, "*.md"))
    pairs = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            pairs.append((os.path.basename(path), f.read()))
    return pairs


def _simple_chunk(text: str, max_tokens: int = 400) -> List[str]:
    chunks = []
    words = text.split()
    buf: List[str] = []
    for w in words:
        buf.append(w)
        if len(buf) >= max_tokens:
            chunks.append(" ".join(buf))
            buf = []
    if buf:
        chunks.append(" ".join(buf))
    return chunks


def _build_index():
    global _index, _chunks, _meta, _embeddings
    file_pairs = _read_kb_files()
    _chunks = []
    _meta = []
    for fname, content in file_pairs:
        for chunk in _simple_chunk(content):
            _chunks.append(chunk)
            _meta.append(fname)
    if not _chunks:
        _index = None
        _embeddings = None
        return

    model = _load_model()
    if model is None:
        # No embeddings backend; rely on token-overlap scoring later
        _index = None
        _embeddings = None
        return

    embeddings = model.encode(_chunks, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
    _embeddings = embeddings
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim) if faiss else None
    if index is not None:
        index.add(embeddings)
    _index = index


def _tokenize_ar(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^\u0600-\u06FF\w\s]", " ", text)  # keep Arabic letters, words, spaces
    toks = re.findall(r"[\u0600-\u06FF\w]+", text)
    return [t for t in toks if len(t) > 1]


def retrieve_references(query: str, top_k: int = 5) -> List[str]:
    global _index, _chunks, _embeddings
    if not _chunks:
        _build_index()
    if not _chunks:
        return []

    model = _load_model()
    if model is None or (_index is None and _embeddings is None):
        # Fallback: token-overlap Jaccard scoring
        q_set = set(_tokenize_ar(query))
        if not q_set:
            return _chunks[:top_k]
        scores = []
        for i, ch in enumerate(_chunks):
            c_set = set(_tokenize_ar(ch))
            inter = len(q_set & c_set)
            union = len(q_set | c_set) or 1
            jacc = inter / union
            scores.append((jacc, i))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [ _chunks[i] for _, i in scores[:top_k] ]

    # Embedding-based
    q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    if _index is not None:
        sims, top_idx = _index.search(q, top_k)
        top_idx = top_idx[0]
        return [ _chunks[i] for i in top_idx if 0 <= i < len(_chunks) ]

    # If FAISS not available, cosine via numpy against precomputed embeddings
    if _embeddings is None:
        return _chunks[:top_k]
    sims = (_embeddings @ q.T).squeeze()
    top_idx = np.argsort(-sims)[:top_k]
    return [ _chunks[i] for i in top_idx if 0 <= i < len(_chunks) ]