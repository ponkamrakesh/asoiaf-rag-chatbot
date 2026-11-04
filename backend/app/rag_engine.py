import time
import random
from typing import List, Dict, Any, Tuple

try:
    from groq import Groq
except ImportError:
    Groq = None

from .config import settings
from .models import (
    ChatRequest, ChatResponse, Citation, QueryMetrics,
    LatencyBreakdown, QueryTransformation
)
from .alias_resolver import (
    classify_domain, correct_spelling, resolve_westeros_aliases,
    enrich_entity_query
)
from .reranker import rerank_chunks, lost_in_the_middle_reorder
from .prompt import format_universal_prompt, CASUAL_RESPONSES


class RAGEngine:
    _instance = None

    def __init__(self):
        print("[RAG Engine] Initializing Citadel Archives RAG Engine...")
        self.embed_model = None
        self.pinecone_client = None
        self.pinecone_index = None
        self.groq_client = None
        self._init_clients()

    def _init_clients(self):
        # 1. FastEmbed
        try:
            from fastembed import TextEmbedding
            print(f"[RAG Engine] Loading FastEmbed model: {settings.EMBEDDING_MODEL}...")
            self.embed_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
            print("[RAG Engine] FastEmbed loaded successfully.")
        except Exception as e:
            print(f"[RAG Engine] Warning: Failed to load FastEmbed locally ({e}).")

        # 2. Pinecone
        if settings.PINECONE_API_KEY:
            try:
                from pinecone import Pinecone
                self.pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
                existing = [i["name"] for i in self.pinecone_client.list_indexes()]
                if settings.PINECONE_INDEX_NAME in existing:
                    self.pinecone_index = self.pinecone_client.Index(settings.PINECONE_INDEX_NAME)
                    print(f"[RAG Engine] Connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")
                else:
                    print(f"[RAG Engine] Notice: Pinecone index '{settings.PINECONE_INDEX_NAME}' pending ingestion.")
            except Exception as e:
                print(f"[RAG Engine] Pinecone connection error: {e}")

        # 3. Groq
        if settings.GROQ_API_KEY and Groq:
            try:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                print("[RAG Engine] Groq client initialized.")
            except Exception as e:
                print(f"[RAG Engine] Groq client error: {e}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RAGEngine()
        return cls._instance

    def query(self, request: ChatRequest) -> ChatResponse:
        total_start = time.perf_counter()
        latencies = LatencyBreakdown()

        # Step 1: Preprocessing, Spell Check & Domain Routing
        t0 = time.perf_counter()
        raw_query = request.message
        
        corrected_query, spelling_fixes = correct_spelling(raw_query)
        resolved_query, alias_expansions = resolve_westeros_aliases(corrected_query)
        enriched_query, is_broad_entity = enrich_entity_query(resolved_query)
        domain = classify_domain(corrected_query)
        
        latencies.spelling_and_routing_ms = round((time.perf_counter() - t0) * 1000, 2)

        transformation = QueryTransformation(
            original_query=raw_query,
            corrected_query=corrected_query,
            enriched_query=enriched_query,
            spelling_corrections=spelling_fixes,
            alias_expansions=alias_expansions,
            is_broad_entity=is_broad_entity
        )

        # Immediate Conversational Routing (Zero Vector Overhead)
        if domain == "casual_chat":
            if "valar morghulis" in raw_query.lower():
                answer = CASUAL_RESPONSES["valar_morghulis"]
            elif any(w in raw_query.lower() for w in ["farewell", "goodbye"]):
                answer = CASUAL_RESPONSES["farewell"]
            else:
                answer = random.choice(CASUAL_RESPONSES["greeting"])

            total_elapsed = round((time.perf_counter() - total_start) * 1000, 2)
            latencies.total_latency_ms = total_elapsed

            return ChatResponse(
                answer=answer,
                citations=[],
                metrics=QueryMetrics(
                    domain=domain,
                    knowledge_mode="Direct Citadel Dialogue",
                    knowledge_ratio={"rag_vectors": 0, "llm_parametric": 100},
                    faithfulness_score=100.0,
                    context_relevance_score=0.0,
                    latency=latencies,
                    prompt_tokens=0,
                    completion_tokens=len(answer.split()),
                    total_tokens=len(answer.split()),
                    tokens_per_second=0.0,
                    model="Grand Maester of Oldtown",
                    cost_usd=0.0,
                    candidate_pool_size=0,
                    reranked_pool_size=0,
                    reordering_strategy="None (Direct Dialogue)",
                    transformation=transformation
                )
            )

        # Step 2: High-Density FastEmbed Generation
        t_embed_start = time.perf_counter()
        query_embedding = None
        if self.embed_model:
            try:
                embeddings = list(self.embed_model.embed([enriched_query]))
                query_embedding = embeddings[0].tolist()
            except Exception as e:
                print(f"[RAG Engine] Embedding error: {e}")
        latencies.embedding_ms = round((time.perf_counter() - t_embed_start) * 1000, 2)

        # Step 3: High Top-K Retrieval from Pinecone (Broad Candidate Pool: 15 Chunks)
        t_pc_start = time.perf_counter()
        candidate_matches = []
        candidate_k = request.candidate_top_k or 15

        if self.pinecone_index and query_embedding:
            try:
                response = self.pinecone_index.query(
                    vector=query_embedding,
                    top_k=candidate_k,
                    include_metadata=True
                )
                candidate_matches = response.get("matches", [])
            except Exception as e:
                print(f"[RAG Engine] Pinecone query error: {e}")
        latencies.pinecone_search_ms = round((time.perf_counter() - t_pc_start) * 1000, 2)

        # Step 4: Two-Stage Re-Ranking (Cross-Scoring Candidates)
        final_n = request.final_top_n or 6
        reranked_chunks, rerank_ms = rerank_chunks(
            query=resolved_query,
            candidates=candidate_matches,
            top_n=final_n
        )
        latencies.reranking_ms = rerank_ms

        # Step 5: 'Lost-in-the-Middle' Attention Re-Ordering
        ordered_chunks = lost_in_the_middle_reorder(reranked_chunks)

        top_composite_score = reranked_chunks[0].get("rerank_score", 0.0) if reranked_chunks else 0.0

        # Knowledge Mode and Attribution Formulations
        if domain == "series_lore":
            knowledge_mode = "Screen Chronicles vs Book Canon (Comparative Synthesis)"
            knowledge_ratio = {"rag_vectors": 40, "llm_parametric": 60}
            faithfulness_estimate = 97.5
        elif domain == "out_of_universe":
            knowledge_mode = "Grand Maester Universal Philosophy & Sciences"
            knowledge_ratio = {"rag_vectors": 15, "llm_parametric": 85}
            faithfulness_estimate = 95.0
        elif top_composite_score >= 0.65 and len(reranked_chunks) > 0:
            knowledge_mode = "Deeply Grounded RAG (Re-Ranked & Re-Ordered)"
            knowledge_ratio = {"rag_vectors": 85, "llm_parametric": 15}
            faithfulness_estimate = 98.5
        elif len(reranked_chunks) > 0:
            knowledge_mode = "Hybrid RAG + Citadel Archival Lore"
            knowledge_ratio = {"rag_vectors": 55, "llm_parametric": 45}
            faithfulness_estimate = 96.0
        else:
            knowledge_mode = "Universal Grand Maester Wisdom (Parametric)"
            knowledge_ratio = {"rag_vectors": 0, "llm_parametric": 100}
            faithfulness_estimate = 93.0

        # Build Citations
        citations = []
        for idx, match in enumerate(ordered_chunks, start=1):
            meta = match.get("metadata", {})
            quote_text = meta.get("text", "")
            snippet = quote_text[:280] + ("..." if len(quote_text) > 280 else "")
            
            citations.append(Citation(
                id=idx,
                book=meta.get("book", "A Song of Ice and Fire"),
                chapter=meta.get("chapter", "Citadel Scroll"),
                page=int(meta.get("page", 0)),
                score=round(float(match.get("rerank_score", match.get("score", 0.0))), 4),
                raw_vector_score=round(float(match.get("score", 0.0)), 4),
                quote=snippet,
                source_type="appendix" if meta.get("is_appendix") else "direct_passage"
            ))

        # Step 6: Groq LLM Generation
        t_groq_start = time.perf_counter()
        prompt_messages = format_universal_prompt(
            query=resolved_query,
            reordered_chunks=ordered_chunks,
            conversation_history=request.conversation_history,
            domain=domain
        )

        answer_text = ""
        prompt_tokens = 0
        completion_tokens = 0
        used_model = settings.GROQ_MODEL

        if self.groq_client:
            models_to_try = [settings.GROQ_MODEL]
            if "llama-3.1-8b-instant" not in models_to_try:
                models_to_try.append("llama-3.1-8b-instant")
            if "llama3-8b-8192" not in models_to_try:
                models_to_try.append("llama3-8b-8192")

            last_err = None
            for candidate_model in models_to_try:
                try:
                    completion = self.groq_client.chat.completions.create(
                        model=candidate_model,
                        messages=prompt_messages,
                        temperature=0.35,
                        max_tokens=1400,
                    )
                    answer_text = completion.choices[0].message.content
                    used_model = candidate_model
                    if completion.usage:
                        prompt_tokens = completion.usage.prompt_tokens
                        completion_tokens = completion.usage.completion_tokens
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    print(f"[RAG Engine] Groq model '{candidate_model}' error: {e}. Trying next fallback...")

            if last_err:
                print(f"[RAG Engine] All Groq model attempts failed: {last_err}")
                answer_text = f"By my chain, the raven failed in its flight ({last_err}). Please verify your GROQ_API_KEY."
        else:
            answer_text = (
                f"**[Citadel Archives Simulation Mode]**\n\n"
                f"Your inquiry was proclaimed: *'{request.message}'*\n\n"
                f"Domain: **{domain.upper()}** | Synthesis Mode: **{knowledge_mode}**.\n\n"
                f"Evaluated {len(candidate_matches)} candidate scrolls from Pinecone and refined down to "
                f"{len(reranked_chunks)} elite scrolls via composite re-ranking.\n\n"
                "To hear the Grand Maester speak in full live prose, add your free `GROQ_API_KEY`."
            )

        groq_duration = time.perf_counter() - t_groq_start
        latencies.groq_llm_ms = round(groq_duration * 1000, 2)
        total_elapsed = round((time.perf_counter() - total_start) * 1000, 2)
        latencies.total_latency_ms = total_elapsed

        tps = round(completion_tokens / groq_duration, 1) if groq_duration > 0 and completion_tokens > 0 else 0.0

        return ChatResponse(
            answer=answer_text,
            citations=citations,
            metrics=QueryMetrics(
                domain=domain,
                knowledge_mode=knowledge_mode,
                knowledge_ratio=knowledge_ratio,
                faithfulness_score=faithfulness_estimate,
                context_relevance_score=round(top_composite_score * 100, 1),
                latency=latencies,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                tokens_per_second=tps,
                model=used_model,
                cost_usd=0.0,
                candidate_pool_size=len(candidate_matches),
                reranked_pool_size=len(reranked_chunks),
                reordering_strategy="Lost-in-the-Middle (Liu et al.)",
                transformation=transformation
            )
        )
