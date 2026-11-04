"""
Test script for Citadel Archives RAG Pipeline
Run queries directly against Pinecone and Groq from CLI.
"""

import os
import sys
import argparse

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models import ChatRequest
from app.rag_engine import RAGEngine


def main():
    parser = argparse.ArgumentParser(description="Query the Citadel Archives RAG Engine")
    parser.add_argument("query", nargs="?", default="Who is Jon Snow?", help="Question to ask")
    args = parser.parse_args()

    print(f"\n==========================================")
    print(f"Archmaester Query: '{args.query}'")
    print(f"==========================================\n")

    engine = RAGEngine.get_instance()
    request = ChatRequest(message=args.query, top_k=5)
    response = engine.query(request)

    print(f"--- ANSWER ---")
    print(response.answer)
    print(f"\n--- CITATIONS ({len(response.citations)}) ---")
    for c in response.citations:
        print(f"[{c.id}] Book: {c.book} | Chapter: {c.chapter} | Page {c.page} | Score: {c.score}")
        print(f"    Quote: \"{c.quote[:150]}...\"\n")

    print(f"--- METRICS ---")
    print(f"Intent: {response.metrics.intent}")
    print(f"Knowledge Mode: {response.metrics.knowledge_mode}")
    print(f"Latency: Total {response.metrics.latency.total_latency_ms}ms "
          f"(Routing: {response.metrics.latency.intent_routing_ms}ms, "
          f"Embedding: {response.metrics.latency.embedding_ms}ms, "
          f"Pinecone: {response.metrics.latency.pinecone_search_ms}ms, "
          f"Groq: {response.metrics.latency.groq_llm_ms}ms)")
    print(f"Tokens: Prompt {response.metrics.prompt_tokens}, Completion {response.metrics.completion_tokens}")


if __name__ == "__main__":
    main()

