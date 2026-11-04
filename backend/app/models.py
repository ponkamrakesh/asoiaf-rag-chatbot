from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class Citation(BaseModel):
    id: int = Field(..., description="Citation marker ID [1], [2], etc.")
    book: str = Field(..., description="Book title (e.g., A Storm of Swords)")
    chapter: str = Field(..., description="POV Chapter or section")
    page: int = Field(..., description="PDF page number")
    score: float = Field(..., description="Re-ranked relevance score (0.0 to 1.0)")
    raw_vector_score: float = Field(default=0.0, description="Raw Pinecone cosine similarity")
    quote: str = Field(..., description="Relevant passage quote from book")
    source_type: str = Field(default="direct_passage", description="'direct_passage' or 'appendix' or 'archival_lore'")


class LatencyBreakdown(BaseModel):
    spelling_and_routing_ms: float = 0.0
    embedding_ms: float = 0.0
    pinecone_search_ms: float = 0.0
    reranking_ms: float = 0.0
    groq_llm_ms: float = 0.0
    total_latency_ms: float = 0.0


class QueryTransformation(BaseModel):
    original_query: str
    corrected_query: str
    enriched_query: str
    spelling_corrections: List[str] = []
    alias_expansions: List[str] = []
    is_broad_entity: bool = False


class QueryMetrics(BaseModel):
    domain: str = Field(..., description="'book_canon', 'series_lore', 'out_of_universe', or 'casual_chat'")
    knowledge_mode: str = Field(..., description="Detailed synthesis mode")
    knowledge_ratio: Dict[str, int] = Field(
        default={"rag_vectors": 50, "llm_parametric": 50},
        description="Percentage split between retrieved RAG chunks and LLM world memory"
    )
    faithfulness_score: float = Field(default=96.0, description="Estimated adherence to book canon (%)")
    context_relevance_score: float = Field(default=0.0, description="Top composite re-rank score (%)")
    latency: LatencyBreakdown
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    tokens_per_second: float = 0.0
    model: str = ""
    cost_usd: float = 0.0
    candidate_pool_size: int = 0
    reranked_pool_size: int = 0
    reordering_strategy: str = "Lost-in-the-Middle"
    transformation: Optional[QueryTransformation] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Recent conversation turns")
    candidate_top_k: Optional[int] = Field(default=15, ge=5, le=30, description="Broad candidate pool from Pinecone")
    final_top_n: Optional[int] = Field(default=6, ge=1, le=10, description="Elite re-ranked chunks fed to LLM")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Grand Maester generated answer with [1], [2] citation markers")
    citations: List[Citation] = Field(default=[], description="List of referenced book sources")
    metrics: QueryMetrics = Field(..., description="Full performance, latency, evaluation, and token metrics")
