from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import ChatRequest, ChatResponse
from .rag_engine import RAGEngine

app = FastAPI(
    title="Citadel Archives: A Song of Ice and Fire RAG Chatbot API",
    description="FastAPI Backend for ASOIAF Pinecone RAG with Groq Llama 3.3 and Deep Citation & Metric Analytics",
    version="1.0.0"
)

# Enable CORS for local dev and cloud frontend hosting (Vercel, Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("[Server] Starting Citadel Archives API...")
    # Pre-warm RAG engine
    RAGEngine.get_instance()


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Citadel Archives ASOIAF RAG API",
        "pinecone_configured": bool(settings.PINECONE_API_KEY),
        "groq_configured": bool(settings.GROQ_API_KEY),
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.GROQ_MODEL
    }


@app.get("/api/health")
def health_check():
    engine = RAGEngine.get_instance()
    return {
        "status": "healthy",
        "pinecone_connected": engine.pinecone_index is not None,
        "groq_connected": engine.groq_client is not None,
        "fastembed_loaded": engine.embed_model is not None,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        engine = RAGEngine.get_instance()
        response = engine.query(request)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API Error] /api/chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Citadel Engine Error: {str(e)}")

