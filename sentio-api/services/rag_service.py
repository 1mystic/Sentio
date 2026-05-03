"""RAG pipeline: embed query → pgvector retrieval → Cohere rerank → return top chunks."""
import os
import logging
import cohere
from typing import Optional
from services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# Lazy-loaded model (avoids import cost at startup)
_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.warning("sentence-transformers not installed — RAG embeddings disabled")
    return _embedder


async def rag_query(
    user_query: str,
    match_threshold: float = 0.65,
    match_count: int = 10,
    rerank_top_n: int = 3,
) -> tuple[str, list[dict]]:
    """
    Run full RAG pipeline.

    Returns:
        (rag_context_string, sources_list)

    Degrades gracefully: if embedder or Cohere is unavailable, returns ("", []).
    """
    embedder = _get_embedder()
    if embedder is None:
        return "", []

    try:
        # 1. Embed the query
        embedding = embedder.encode(user_query).tolist()

        # 2. Retrieve via pgvector (Supabase RPC)
        supabase = get_supabase()
        results = supabase.rpc('match_knowledge', {
            'query_embedding': embedding,
            'match_threshold': match_threshold,
            'match_count': match_count,
        }).execute()

        if not results.data:
            logger.debug("No knowledge articles matched query")
            return "", []

        documents = results.data

        # 3. Rerank with Cohere (if API key available)
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key and len(documents) > rerank_top_n:
            try:
                co = cohere.Client(cohere_key)
                reranked = co.rerank(
                    query=user_query,
                    documents=[d['content'] for d in documents],
                    top_n=rerank_top_n,
                    model="rerank-english-v2.0",
                )
                top_docs = [documents[r.index] for r in reranked.results]
            except Exception as e:
                logger.warning(f"Cohere rerank failed, using top-{rerank_top_n} by similarity: {e}")
                top_docs = documents[:rerank_top_n]
        else:
            top_docs = documents[:rerank_top_n]

        # 4. Build context string
        context_parts = []
        for i, doc in enumerate(top_docs, 1):
            citation = doc.get('source_citation', doc.get('title', 'Psychology Knowledge Base'))
            context_parts.append(f"[Source {i}: {citation}]\n{doc['content']}")

        rag_context = "\n\n".join(context_parts)
        sources = [
            {"title": d.get("title", ""), "citation": d.get("source_citation", "")}
            for d in top_docs
        ]

        return rag_context, sources

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return "", []


async def embed_and_store_article(
    title: str,
    content: str,
    category: Optional[str] = None,
    source_citation: Optional[str] = None,
    source_url: Optional[str] = None,
) -> bool:
    """Embed a single article chunk and store in knowledge_articles table."""
    embedder = _get_embedder()
    if embedder is None:
        return False
    try:
        embedding = embedder.encode(content).tolist()
        get_supabase().table("knowledge_articles").insert({
            "title": title,
            "content": content,
            "category": category,
            "source_citation": source_citation,
            "source_url": source_url,
            "embedding": embedding,
        }).execute()
        return True
    except Exception as e:
        logger.error(f"embed_and_store_article error: {e}")
        return False
