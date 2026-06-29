def retrieve(query: str, chunks: list[str], top_k: int = 4) -> list[str]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        docs = [query] + chunks
        vec = TfidfVectorizer(stop_words="english")
        mat = vec.fit_transform(docs)
        scores = cosine_similarity(mat[0:1], mat[1:]).flatten()
        indices = np.argsort(scores)[::-1][:top_k]
        return [chunks[i] for i in indices if scores[i] > 0]
    except ImportError:
        # Fallback: keyword overlap
        qw = set(query.lower().split())
        scored = sorted(
            ((len(qw & set(c.lower().split())), c) for c in chunks),
            reverse=True,
        )
        return [c for s, c in scored[:top_k] if s > 0]
