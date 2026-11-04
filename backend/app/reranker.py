"""
Two-Stage Re-Ranking & 'Lost-in-the-Middle' Context Re-Ordering Module
Filters Top-K candidates (e.g. 15-20) down to the elite Top-N chunks (e.g. 6),
and re-orders them to maximize LLM attention and narrative coherence.
"""

import time
import math
import re
from typing import List, Dict, Any, Tuple


def calculate_lexical_overlap(query: str, text: str) -> float:
    """Computes keyword and entity co-occurrence score between query and chunk."""
    query_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower()))
    if not query_tokens:
        return 0.0
    text_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    intersection = query_tokens.intersection(text_tokens)
    return len(intersection) / len(query_tokens)


def rerank_chunks(
    query: str,
    candidates: List[Dict[str, Any]],
    top_n: int = 6,
    vector_weight: float = 0.65,
    lexical_weight: float = 0.35
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Two-stage Re-ranking:
    Combines dense Pinecone vector similarity with exact lexical/entity overlap,
    chronological relevance, and appendix boost.
    """
    t0 = time.perf_counter()
    if not candidates:
        return [], 0.0

    scored_candidates = []

    for item in candidates:
        vector_score = float(item.get("score", 0.0))
        meta = item.get("metadata", {})
        text = meta.get("text", "")
        chapter = meta.get("chapter", "").upper()
        
        # 1. Lexical overlap score
        lexical_score = calculate_lexical_overlap(query, text)
        
        # 2. Entity / Chapter header bonus
        header_bonus = 0.0
        query_words = set(query.upper().split())
        if chapter in query_words:
            header_bonus = 0.15

        # 3. Appendix boost for broad questions
        appendix_bonus = 0.08 if meta.get("is_appendix") and any(w in query.lower() for w in ["who", "what", "house", "lineage", "family"]) else 0.0

        # Composite score
        composite_score = (
            (vector_score * vector_weight) +
            (lexical_score * lexical_weight) +
            header_bonus +
            appendix_bonus
        )

        item["rerank_score"] = round(min(composite_score, 1.0), 4)
        scored_candidates.append(item)

    # Sort descending by composite score
    scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    selected_pool = scored_candidates[:top_n]

    duration_ms = round((time.perf_counter() - t0) * 1000, 2)
    return selected_pool, duration_ms


def lost_in_the_middle_reorder(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Re-orders chunks according to the 'Lost in the Middle' cognitive principle (Liu et al.):
    LLMs attend most strongly to the start and end of the context window, and often
    skip or de-prioritize information placed in the middle.

    Pattern:
    Rank 1 -> Position 1 (Start)
    Rank 2 -> Position Last (End)
    Rank 3 -> Position 2
    Rank 4 -> Position Second to Last
    ...
    """
    if len(chunks) <= 2:
        return chunks

    reordered = [None] * len(chunks)
    left = 0
    right = len(chunks) - 1

    for idx, chunk in enumerate(chunks):
        if idx % 2 == 0:
            reordered[left] = chunk
            left += 1
        else:
            reordered[right] = chunk
            right -= 1

    return [c for c in reordered if c is not None]

