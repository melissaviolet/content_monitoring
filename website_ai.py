from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_monitoring.settings")

import django

django.setup()

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from monitoring.models import ContentItem, Flag

MODEL_NAME = "qwen3:4b"
EMBEDDING_MODEL = "qwen3:4b"
VECTOR_DIR = Path(__file__).resolve().parent / "vector_store"

embeddings = None
try:
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
except Exception:
    embeddings = None


def build_vector_store() -> Chroma | None:
    if embeddings is None:
        return None

    return Chroma(
        collection_name="content_monitoring",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DIR),
    )


def _serialize_content_item(item: ContentItem) -> str:
    matching_flags = Flag.objects.filter(content_item=item).select_related("keyword")
    flag_summary = ", ".join(
        f"{flag.keyword.name} ({flag.status}, score={flag.score})"
        for flag in matching_flags
    )
    if not flag_summary:
        flag_summary = "no flags"

    return (
        f"Article: {item.title}\n"
        f"Source: {item.source}\n"
        f"Updated: {item.last_updated}\n"
        f"Flags: {flag_summary}\n"
        f"Body: {item.body}"
    )


def ensure_vector_index() -> Chroma | None:
    vector_store = build_vector_store()
    if vector_store is None:
        return None

    docs = list(ContentItem.objects.all().order_by("-last_updated"))
    if not docs:
        return vector_store

    try:
        existing_count = vector_store._collection.count()
    except Exception:
        existing_count = 0

    if existing_count == 0:
        chunks = []
        for item in docs:
            chunks.append(
                {
                    "id": str(item.id),
                    "text": _serialize_content_item(item),
                    "metadata": {
                        "title": item.title,
                        "source": item.source,
                        "id": item.id,
                    },
                }
            )
        try:
            vector_store.add_texts(
                texts=[chunk["text"] for chunk in chunks],
                ids=[chunk["id"] for chunk in chunks],
                metadatas=[chunk["metadata"] for chunk in chunks],
            )
        except Exception:
            return None

    return vector_store


def get_context(question: str, limit: int = 5) -> str:
    vector_store = ensure_vector_index()
    if vector_store is None:
        return (
            "No embedding model is available yet. "
            "Please ensure Ollama is running with embedding support or use the fallback chatbot flow."
        )

    try:
        docs = vector_store.similarity_search(question, k=limit)
    except Exception:
        docs = []

    if not docs:
        return (
            "No relevant content was found. "
            "Try importing content or adjusting your question."
        )

    return "\n\n".join(doc.page_content for doc in docs)


template = """
You are a helpful assistant for a content monitoring dashboard.
Use only the context below to answer the user's question.
If the answer is not in the context, say that you do not have enough information.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(template)


def build_chain():
    try:
        llm = ChatOllama(model=MODEL_NAME, temperature=0)
    except Exception as exc:
        raise RuntimeError(
            "ChatOllama is unavailable. Install langchain-ollama and ensure Ollama is running."
        ) from exc
    return prompt | llm


def main() -> None:
    chain = build_chain()
    while True:
        print("\n\n-------------------------------------------------------------------------------")
        question = input("Ask a question (q to quit): ").strip()
        print("\n")

        if question.lower() in {"q", "quit", "exit"}:
            break

        context = get_context(question)
        result = chain.invoke({"context": context, "question": question})
        answer = result.content if hasattr(result, "content") else str(result)
        print(answer)


if __name__ == "__main__":
    main()

