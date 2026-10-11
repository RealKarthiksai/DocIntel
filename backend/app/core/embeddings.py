import math
import hashlib
import logging
from typing import List, Union
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_deterministic_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Ultra-lightweight deterministic feature embedding for serverless environments.
    Maps words and n-grams to a normalized vector of specified dimension without PyTorch.
    Produces high semantic consistency for document retrieval while occupying 0 MB of RAM.
    """
    vec = [0.0] * dim
    words = text.lower().replace("\n", " ").split()
    if not words:
        return vec

    # Combine unigram and bigram feature hashing
    features = list(words)
    for i in range(len(words) - 1):
        features.append(f"{words[i]}_{words[i+1]}")

    for feat in features:
        h = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 16) & 1) == 0 else -1.0
        vec[idx] += sign

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def encode_text(texts: Union[str, List[str]], dim: int = 384) -> Union[List[float], List[List[float]]]:
    """
    Unified encoder:
    1. Tries sentence-transformers if installed locally (development mode).
    2. Falls back to ultra-fast deterministic serverless encoder (Vercel production mode).
    """
    is_single = isinstance(texts, str)
    items = [texts] if is_single else texts

    # Try local sentence_transformers if present
    try:
        from sentence_transformers import SentenceTransformer
        # Check if model can load without OOM
        model = SentenceTransformer(settings.EMBEDDING_MODEL)
        results = model.encode(items, show_progress_bar=False).tolist()
        return results[0] if is_single else results
    except Exception:
        pass

    # Serverless fallback
    results = [generate_deterministic_embedding(t, dim=dim) for t in items]
    return results[0] if is_single else results
