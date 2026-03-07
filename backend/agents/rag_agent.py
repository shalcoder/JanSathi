"""
rag_agent.py — Agent 3: RAG Knowledge Retrieval
================================================
Responsibilities:
  - Retrieve relevant scheme information from the knowledge base
  - Combine results from local TF-IDF + Kendra (when available)
  - Populate state["rag_context"] with top scheme chunks

Production upgrade path:
  - Replace local TF-IDF with Amazon Bedrock Knowledge Base
  - Set BEDROCK_KB_ID env var to use managed vector RAG
"""
import os
import logging

from .state import JanSathiState

logger = logging.getLogger(__name__)

# ── Bedrock Knowledge Base (production managed RAG) ───────────────────────────
BEDROCK_KB_ID = os.getenv("BEDROCK_KB_ID", "")


def rag_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 3: RAG Knowledge Agent.
    Retrieves scheme context for the user's query and scheme_hint.
    """
    session_id = state.get("session_id", "unknown")
    query = state.get("user_query", "")
    language = state.get("language", "hi")
    scheme_hint = state.get("scheme_hint", "unknown")
    slots = state.get("slots", {})

    logger.info(f"[RAGAgent] session={session_id} scheme={scheme_hint} query='{query[:60]}'")

    # Enrich query with scheme hint for better retrieval
    enriched_query = f"{scheme_hint.replace('_', ' ')} {query}" if scheme_hint != "unknown" else query
    user_profile = {**slots, "scheme": scheme_hint}

    context_chunks = []

    # ── Option A: Bedrock Knowledge Base (Production) ─────────────────────────
    if BEDROCK_KB_ID:
        context_chunks = _retrieve_from_bedrock_kb(enriched_query, BEDROCK_KB_ID)
        logger.info(f"[RAGAgent] Bedrock KB returned {len(context_chunks)} chunks")

    # ── Option B: Local RagService (Development) ──────────────────────────────
    if not context_chunks:
        context_chunks = _retrieve_from_local_rag(enriched_query, language, user_profile)
        logger.info(f"[RAGAgent] Local RAG returned {len(context_chunks)} chunks")

    # ── Fallback ──────────────────────────────────────────────────────────────
    if not context_chunks:
        context_chunks = [
            f"General information about {scheme_hint.replace('_', ' ')} scheme. "
            "Please visit india.gov.in or myscheme.gov.in for complete details."
        ]

    updated = dict(state)
    updated["rag_context"] = context_chunks
    return updated


def _retrieve_from_bedrock_kb(query: str, kb_id: str) -> list:
    """Query Amazon Bedrock Knowledge Base using the retrieve API."""
    try:
        import boto3
        region = os.getenv("AWS_REGION", "us-east-1")
        client = boto3.client("bedrock-agent-runtime", region_name=region)
        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": 4}
            },
        )
        chunks = []
        for item in response.get("retrievalResults", []):
            text = item.get("content", {}).get("text", "")
            source = item.get("location", {}).get("s3Location", {}).get("uri", "")
            if text:
                chunks.append(f"{text} [Source: {source}]" if source else text)
        return chunks
    except Exception as e:
        logger.warning(f"[RAGAgent] Bedrock KB retrieval failed: {e}")
        return []


def _retrieve_from_local_rag(query: str, language: str, user_profile: dict) -> list:
    """Use existing local RagService (TF-IDF + SQLite scheme DB)."""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.services.rag_service import RagService
        rag = RagService()
        results = rag.retrieve(query, language=language, user_profile=user_profile)
        return results if isinstance(results, list) else []
    except Exception as e:
        logger.warning(f"[RAGAgent] Local RAG failed: {e}")
        return []
