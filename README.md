# ⚔️ Citadel Archives: A Song of Ice and Fire RAG Chatbot

An end-to-end, production-grade Retrieval-Augmented Generation (RAG) system built across all 5 books of George R. R. Martin's *A Song of Ice and Fire* (4,068 pages, 1.77 million words), backed by **Pinecone Vector DB**, **Groq LPU (Llama 3.3 70B)**, a **FastAPI backend**, and a **React (Vite + Tailwind CSS) frontend** with real-time Citations and a switchable Metrics Dashboard.

**100% Free Hosting Stack**:
- **Vector DB**: Pinecone Serverless Free Tier
- **LLM Inference**: Groq Cloud Free Tier (`llama-3.3-70b-versatile`)
- **Embeddings**: FastEmbed (`BAAI/bge-small-en-v1.5`, 384 dimensions) running locally on CPU in GitHub Actions
- **Ingestion**: GitHub Actions (Ubuntu runner, 2,000 free minutes/mo)
- **Backend**: Render.com Free Web Service (or Hugging Face Spaces)
- **Frontend**: Vercel (or Netlify)

---

## 🏛️ System Architecture

```
[got.pdf in GitHub: data/got.pdf]
                │
                ▼ (GitHub Actions Ingestion)
[PyMuPDF Parsing ➔ Book & POV Chapter Splitter ➔ FastEmbed CPU]
                │
                ▼ (Batch Upsert)
      [Pinecone Serverless Vector DB]
                ▲
                │ Vector Retrieval
                ▼
      [FastAPI Backend Engine]
        ├── 1. Intent Router (Chit-chat vs Lore query)
        ├── 2. Westeros Alias Resolver ("Kingslayer" ➔ "Jaime Lannister")
        ├── 3. Dual-Stream Retrieval (Narrative Chunks + Biographical Appendices)
        ├── 4. Groq LLM (Llama 3.3 70B with Citadel Archmaester System Prompt)
        └── 5. Latency & Token Metrics Calculator
                ▲
                │ REST API / CORS
                ▼
      [React + Vite Frontend]
        ├── ⚔️ Chat Window (Markdown answers + [1], [2] citation badges)
        ├── 📜 Citations Panel (Live book quote, POV chapter, page #, match %)
        └── 📊 Metrics Dashboard (Mode switch: Latency waterfall, token costs, similarity bars)
```

---

## 🚀 Quick Setup & Deployment Guide

### Step 1: Upload Repository to GitHub
1. Create a new repository on [GitHub](https://github.com/new) (e.g. `asoiaf-rag-chatbot`).
2. Initialize and push your repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Citadel Archives ASOIAF RAG"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/asoiaf-rag-chatbot.git
   git push -u origin main
   ```

---

### Step 2: Configure Free Pinecone & GitHub Secrets
1. Go to [Pinecone.io](https://www.pinecone.io/) and create a free account.
2. In Pinecone Console, get your **API Key**. (Index will be automatically created with 384 dimensions and cosine metric by the ingestion script, or create an index named `asoiaf-books` with dimension `384` and metric `cosine`).
3. In your GitHub repository, navigate to **Settings > Secrets and variables > Actions > New repository secret**:
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `PINECONE_INDEX_NAME`: `asoiaf-books`
4. Trigger the ingestion:
   - Go to the **Actions** tab in GitHub.
   - Click **Ingest ASOIAF to Pinecone** > **Run workflow**.
   - GitHub Actions will parse `data/got.pdf`, embed all chunks via FastEmbed, and upsert them to Pinecone for free.

---

### Step 3: Deploy Backend to Render.com (100% Free)
1. Sign up at [Render.com](https://render.com/).
2. Click **New + > Web Service** and connect your GitHub repository.
3. Configure the service:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. In **Environment Variables**, add:
   - `PINECONE_API_KEY`: your Pinecone API key
   - `PINECONE_INDEX_NAME`: `asoiaf-books`
   - `GROQ_API_KEY`: your Groq free API key from [console.groq.com](https://console.groq.com)
   - `GROQ_MODEL`: `llama-3.3-70b-versatile`
5. Click **Create Web Service**. Render will generate your public API URL (e.g., `https://asoiaf-rag-backend.onrender.com`).

---

### Step 4: Deploy Frontend to Vercel (100% Free)
1. Sign up at [Vercel.com](https://vercel.com/).
2. Click **Add New... > Project** and select your GitHub repository.
3. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Environment Variables**:
     - `VITE_API_URL`: Your Render backend URL (e.g. `https://asoiaf-rag-backend.onrender.com`)
4. Click **Deploy**. Vercel will build and assign your free live URL (e.g., `https://asoiaf-rag.vercel.app`).

---

## 💻 Local Development

### 1. Run Backend Locally
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Create .env file with your keys
echo GROQ_API_KEY=your_key >> .env
echo PINECONE_API_KEY=your_key >> .env
echo PINECONE_INDEX_NAME=asoiaf-books >> .env

uvicorn app.main:app --reload --port 8000
```

### 2. Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 High-Level RAG Facilities Implemented

- **Intent Routing & Chit-Chat Bypass**: Queries like *"Hi Grand Maester"* trigger an immediate in-character greeting without wasting vector search queries or generating irrelevant book trivia.
- **Westeros Alias Resolution**: Resolves titles like *"The Kingslayer"*, *"The Imp"*, *"The Onion Knight"*, *"The Hound"* into canonical names before embedding.
- **Dual-Stream Biographical Retrieval**: Broad questions like *"Who is Jon Snow?"* retrieve from both narrative chapters and official book appendices to synthesize complete biographical overviews.
- **Strict Book Canon Prompting**: Completely shields responses from HBO television adaptation changes (preserves Lady Stoneheart, Aegon VI / Young Griff, Jeyne Poole).
- **Interactive Inline Citations**: Every claim is tagged with `[1]`, `[2]`. Clicking an inline badge highlights the exact book quote, POV chapter, and page number in the citations drawer.
- **Full Metrics Switch View**: Switch to the **Metrics Dashboard** tab to inspect latency waterfall breakdowns, Pinecone cosine similarity distributions, token counts, and raw retrieved chunks.

