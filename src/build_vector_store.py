"""Build and persist the Chroma vector store for care documents."""

from pathlib import Path

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ModuleNotFoundError:  # pragma: no cover - compatibility for newer LangChain installs
    from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import CHROMA_DIR, EMBEDDING_MODEL_NAME
from .load_data import load_markdown_documents


def build_vector_store(persist_directory: Path | None = None) -> Chroma:
    """Load markdown documents, chunk them, and persist embeddings."""

    persist_path = persist_directory or CHROMA_DIR
    persist_path.mkdir(parents=True, exist_ok=True)

    documents = load_markdown_documents()
    if not documents:
        raise ValueError("No care documents found. Generate data before building the vector store.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    split_docs = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    store = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=str(persist_path),
    )
    store.persist()
    return store


if __name__ == "__main__":
    build_vector_store()
    print(f"Chroma vector store created/updated at {CHROMA_DIR}.")