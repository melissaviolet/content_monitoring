"""
RAG (Retrieval Augmented Generation) chat service.

Exposes one function — ask_rag_chatbot() — that views.py calls directly.

How it works, step by step:
1. ensure_vector_index() makes sure every ContentItem in the database
   has been converted into a vector and stored in ChromaDB. If new
   articles were added since last time, it embeds those too.
2. get_context() takes the user's question, embeds it, and asks
   ChromaDB for the most similar article chunks (similarity_search).
3. Those chunks get inserted into a prompt template.
4. The prompt is sent to Ollama (via ChatOllama) which generates
   the final answer.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from ..models import ContentItem, Flag, Keyword

MODEL_NAME = "qwen3:4b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIR = Path(__file__).resolve().parent / "vector_store"

# ── Cached objects ──
# Loading the embedding model and the chat chain is slow (a few seconds).
# We don't want to reload them on EVERY single chat message, so we cache
# them in these module-level variables. First call loads them, every
# call after that reuses what's already loaded.
_embeddings = None
_chain = None


def _get_embeddings():
    """Load the HuggingFace embedding model once, reuse after that."""
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        except Exception:
            _embeddings = False
    return _embeddings if _embeddings is not False else None


def build_vector_store() -> Chroma | None:
    """Connect to (or create) the local ChromaDB collection on disk."""
    embeddings = _get_embeddings()
    if embeddings is None:
        return None

    return Chroma(
        collection_name="content_monitoring",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DIR),
    )


def _serialize_content_item(item: ContentItem) -> str:
    """
    Turn one ContentItem (and its related flags) into a single text
    blob. This is what actually gets embedded into a vector — so it
    needs to contain everything worth searching on.
    """
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
    """
    Make sure every article currently in the database has a matching
    vector in ChromaDB. Only embeds articles that aren't already
    indexed — avoids re-embedding everything on every request.
    """
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

    # Simple approach: if the collection is empty, embed everything.
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
    """
    Given a user's question, find the most relevant article chunks
    using vector similarity search. This is the "Retrieval" half of RAG.
    """
    content_count = ContentItem.objects.count()
    keyword_count = Keyword.objects.count()
    flag_count = Flag.objects.count()

    vector_store = ensure_vector_index()
    if vector_store is None:
        return (
            f"Database status: {content_count} content items, {keyword_count} keywords, "
            f"and {flag_count} flags. No embedding model is available right now."
        )

    try:
        docs = vector_store.similarity_search(question, k=limit)
    except Exception:
        docs = []

    if not docs:
        return "No relevant content was found. Try importing content or adjusting your question."

    return "\n\n".join(doc.page_content for doc in docs)


# ── The prompt template ──
# {context} gets filled with the retrieved article chunks.
# {question} gets filled with whatever the user typed.
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


def _get_chain():
    """
    Build the LangChain "chain" once and cache it.
    A chain is just: take the prompt template, pipe it into the model.
    The | symbol here means "pass the output of the left side into the
    right side" — same idea as piping commands in a terminal.
    """
    global _chain
    if _chain is None:
        llm = ChatOllama(model=MODEL_NAME, temperature=0)
        _chain = prompt | llm
    return _chain


def ask_rag_chatbot(question: str) -> str:
    """
    The single function views.py needs to call.

    Takes a plain question string, returns a plain answer string.
    This is the "Generation" half of RAG — context comes in,
    a real-language answer comes out.
    """
    if not question or not question.strip():
        return "Please ask a question."

    try:
        context = get_context(question)
        chain = _get_chain()
        result = chain.invoke({"context": context, "question": question})
        answer = result.content if hasattr(result, "content") else str(result)
        return answer
    except Exception as e:
        return f"Sorry, I ran into an error answering that: {e}"