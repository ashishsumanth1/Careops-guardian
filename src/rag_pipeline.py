"""Retrieval-augmented generation pipeline for service-user-specific answers."""

from typing import Any

try:
    from langchain.chains import RetrievalQA
except ModuleNotFoundError:  # pragma: no cover - compat fallback
    RetrievalQA = None  # type: ignore[assignment]

try:
    from langchain.prompts import PromptTemplate
except ModuleNotFoundError:  # pragma: no cover
    from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import CHROMA_DIR, CHAT_MODEL_NAME, EMBEDDING_MODEL_NAME


if RetrievalQA is None:  # pragma: no cover - fallback shim
    class RetrievalQA:  # type: ignore[override]
        """Minimal shim replicating RetrievalQA.invoke for simple stuffing chains."""

        def __init__(self, llm: ChatOpenAI, retriever: Any, prompt: PromptTemplate):
            self.llm = llm
            self.retriever = retriever
            self.prompt = prompt

        @classmethod
        def from_chain_type(
            cls,
            *,
            llm: ChatOpenAI,
            retriever: Any,
            chain_type: str,
            chain_type_kwargs: dict | None = None,
            return_source_documents: bool | None = None,
        ) -> "RetrievalQA":
            prompt = (chain_type_kwargs or {}).get("prompt")
            if prompt is None:
                raise ValueError("Prompt must be supplied in chain_type_kwargs when using fallback RetrievalQA shim.")
            return cls(llm=llm, retriever=retriever, prompt=prompt)

        def invoke(self, inputs: dict) -> dict:
            question = inputs.get("question", "")
            service_user_id = inputs.get("service_user_id", "")
            docs = self.retriever.invoke(question)
            context = "\n\n---\n\n".join(doc.page_content for doc in docs) if docs else "No matching documents retrieved."
            prompt_text = self.prompt.format(
                context=context,
                service_user_id=service_user_id,
                question=question,
            )
            response = self.llm.invoke(prompt_text)
            content = getattr(response, "content", response)
            return {"result": content}


def get_vector_store() -> Chroma:
    """Initialise Chroma vector store using persisted embeddings."""

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    return Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)


def get_retriever_for_service_user(service_user_id: str):
    """Return a retriever filtered to a specific service user."""

    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 6,
            "filter": {"service_user_id": {"$eq": service_user_id.upper()}},
        }
    )
    return retriever


def answer_question(service_user_id: str, question: str) -> str:
    """Run a RetrievalQA chain and return the answer text."""

    retriever = get_retriever_for_service_user(service_user_id)
    llm = ChatOpenAI(model=CHAT_MODEL_NAME, temperature=0)

    prompt = PromptTemplate(
        input_variables=["context", "service_user_id", "question"],
        template=(
            "You are CareOps Guardian, an assistant supporting domiciliary care managers.\n"
            "Use only the context from care plans and risk assessments for the given service user.\n"
            "Service user ID: {service_user_id}\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer in clear UK English, summarising relevant instructions and risks. "
            "If information is not available, say so."
        ),
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )

    result: Any = qa_chain.invoke({
        "service_user_id": service_user_id,
        "question": question,
    })

    if isinstance(result, dict) and "result" in result:
        return result["result"]
    return str(result)


if __name__ == "__main__":
    response = answer_question("SU001", "What support is required with transfers and falls risk")
    print(response)
