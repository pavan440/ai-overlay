import os


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise RuntimeError("pypdf not installed — run: pip install pypdf")
    if ext in (".docx", ".doc"):
        try:
            from docx import Document
            return "\n".join(p.text for p in Document(path).paragraphs)
        except ImportError:
            raise RuntimeError("python-docx not installed — run: pip install python-docx")
    # Plain text fallback (txt, md, py, js, …)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()
