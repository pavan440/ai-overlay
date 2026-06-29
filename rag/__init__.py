import os

from .chunker import chunk_text
from .extractor import extract_text
from .retriever import retrieve


class DocumentStore:
    def __init__(self) -> None:
        self._docs: dict[str, list[str]] = {}   # filename → chunks

    def add(self, path: str) -> int:
        text = extract_text(path)
        chunks = chunk_text(text)
        self._docs[os.path.basename(path)] = chunks
        return len(chunks)

    def remove(self, name: str) -> None:
        self._docs.pop(name, None)

    def clear(self) -> None:
        self._docs.clear()

    def names(self) -> list[str]:
        return list(self._docs.keys())

    def get_context(self, query: str, top_k: int = 4) -> str:
        all_chunks = [c for chunks in self._docs.values() for c in chunks]
        if not all_chunks:
            return ""
        relevant = retrieve(query, all_chunks, top_k)
        if not relevant:
            return ""
        return "Context from uploaded documents:\n\n" + "\n\n---\n\n".join(relevant)

    @property
    def has_docs(self) -> bool:
        return bool(self._docs)

    @property
    def chunk_count(self) -> int:
        return sum(len(c) for c in self._docs.values())


__all__ = ["DocumentStore"]
