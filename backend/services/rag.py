"""
Pinecone precedent RAG — fully optional. If PINECONE_API_KEY is unset the
query returns [] and Wingman still works end-to-end.
"""
from config import settings

_index = None


def _get_index():
    global _index
    if _index is not None:
        return _index
    if not settings.pinecone_api_key:
        return None
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        _index = pc.Index(settings.pinecone_index)
        return _index
    except Exception:
        return None


async def query_precedents(query: str, top_k: int = 5) -> list:
    index = _get_index()
    if index is None:
        return []
    try:
        # Placeholder: embeddings would be generated here in production.
        return []
    except Exception:
        return []


async def ingest_precedent(text: str, metadata: dict):
    index = _get_index()
    if index is None:
        return
    # Production: embed + upsert.
