"""Utilities to load markdown documents with LangChain loaders."""

from pathlib import Path
from typing import List

try:  # LangChain >=1.0 relocates Document; retain backward-compat import first
    from langchain.docstore.document import Document
except ModuleNotFoundError:  # pragma: no cover - fallback for newer versions
    from langchain_core.documents import Document

from langchain_community.document_loaders import TextLoader

from .config import CARE_PLANS_DIR, RISK_ASSESSMENTS_DIR


def _derive_service_user_id(path: Path) -> str:
    """Extract service user ID from filename (e.g., su001_care_plan.md -> SU001)."""
    stem_parts = path.stem.split("_")
    if not stem_parts:
        return "UNKNOWN"
    candidate = stem_parts[0].upper()
    if candidate.startswith("SU") and len(candidate) == 5:
        return candidate
    return candidate


def _risk_category_from_path(path: Path) -> str:
    """Infer risk category from filename suffix."""
    stem = path.stem
    if stem.endswith("_risk"):
        parts = stem.split("_")
        if len(parts) >= 2:
            return parts[-2]
    return "general"


def load_markdown_documents() -> List[Document]:
    """Load care plans and risk assessments into LangChain Document objects."""

    documents: List[Document] = []
    search_paths = [CARE_PLANS_DIR, RISK_ASSESSMENTS_DIR]

    for base_dir in search_paths:
        for path in base_dir.rglob("*.md"):
            loader = TextLoader(str(path), encoding="utf-8")
            loaded_docs = loader.load()
            for doc in loaded_docs:
                service_user_id = _derive_service_user_id(path)
                doc.metadata.setdefault("source", str(path))
                doc.metadata["service_user_id"] = service_user_id
                if CARE_PLANS_DIR in path.parents:
                    doc.metadata["doc_type"] = "care_plan"
                elif RISK_ASSESSMENTS_DIR in path.parents:
                    doc.metadata["doc_type"] = "risk_assessment"
                    doc.metadata["risk_category"] = _risk_category_from_path(path)
                documents.append(doc)
    return documents


if __name__ == "__main__":
    docs = load_markdown_documents()
    print(f"Loaded {len(docs)} markdown documents.")
    for example in docs[:2]:
        print(example.metadata)
