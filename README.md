# LORAN Memories Retriever

A complete end-to-end system for personal memory retrieval using a custom-trained neural retrieval model. This project demonstrates the full machine learning pipeline from model architecture design, large-scale pre-training on MSMARCO, synthetic data generation, domain-specific finetuning, to production deployment in a real-world application.

## Table of Contents

- [Overview](#overview)
- [Model Architecture](#model-architecture)
- [Memories Retrieval Application](#memories-retrieval-application)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)

## Overview

This project implements a complete retrieval system for personal memories (photos, videos, audio) using natural language queries. The core innovation is the **LORAN** architecture - a lightweight neural retrieval model that combines lexical matching with semantic understanding through a unique multi-vector late interaction mechanism.

**Key Highlights:**

- Custom neural architecture optimized for retrieval tasks
- Large-scale pre-training on MSMARCO v2.1 (500K+ query-document pairs)
- Multi-GPU distributed training with PyTorch DDP
- Automated synthetic data generation using Vertex AI Gemini-2.5-Pro
- Domain-specific finetuning on memory retrieval data
- Production-ready FastAPI backend with Vertex AI agents and ZEP-Graphiti knowledge graphs
- Modern React frontend with streaming AI chat interface

### System Architecture

```
┌─────────────────────┐
│   React Frontend    │
│  (TypeScript/Vite)  │
└──────────┬──────────┘
           │ REST API + SSE
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│   (Python 3.10+)    │
└──────────┬──────────┘
           │
    ┌──────┴──────────────────────┐
    │                             │
    ▼                             ▼
┌──────────────┐          ┌──────────────┐
│  Vertex AI   │          │     ZEP      │
│    Agent     │          │   Graphiti   │
│ (Gemini 2.0) │          │ (Memory Graph)│
└──────┬───────┘          └──────┬───────┘
       │                         │
       ▼                         ▼
┌──────────────┐          ┌──────────────┐
│  LORAN  │          │    Neo4j     │
│   Embeddings │          │  Graph DB    │
└──────┬───────┘          └──────────────┘
       │
       ▼
┌──────────────┐
│ Google Cloud │
│   Storage    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│   Database   │
└──────────────┘
```

### Backend Features

1. **LORAN Integration**
   - Custom trained model for semantic search
   - Fast vector similarity search with FAISS
   - Multi-vector query representations

2. **Vertex AI Agent (ADK)**
   - Natural language conversation interface
   - Context-aware memory retrieval
   - Streaming responses via Server-Sent Events (SSE)

3. **ZEP-Graphiti Knowledge Graph**
   - Connected memory exploration
   - Temporal and relational context
   - Neo4j-backed graph storage

4. **Media Management**
   - Google Cloud Storage integration
   - Face detection and annotation
   - Photo, video, audio support

5. **RESTful API**
   - Memory upload and management
   - Semantic search endpoints
   - Agent chat interface
   - Session management

### Frontend Features

1. **Memory Palace Interface**
   - Conversational AI chat
   - Natural language queries
   - Real-time streaming responses

2. **Memory Management**
   - Upload photos, videos, audio
   - Add captions and descriptions
   - View and organize memories

3. **Semantic Search**
   - Natural language search
   - Results ranked by LORAN model
   - Preview and full-view modes

4. **Modern UI**
   - React 18 + TypeScript
   - TailwindCSS styling
   - Responsive design
   - Radix UI components

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy + PostgreSQL (data persistence)
- Vertex AI + ADK (AI agents)
- ZEP + Graphiti (knowledge graphs)
- Neo4j (graph database)
- Sentence Transformers (embeddings)
- Google Cloud Storage (media files)

**Frontend:**
- React 18
- TypeScript
- Vite (build tool)
- TailwindCSS 3
- React Router 6
- Server-Sent Events (SSE)

### Quick Start

**Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run server
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to access the application.

### API Endpoints

- `POST /api/chat` - Stream chat with AI agent
- `POST /api/memories/search` - Semantic search
- `POST /api/upload/photo` - Upload photo with metadata
- `GET /api/memories` - List all memories
- `GET /api/health` - Health check

## Project Structure

```
Memories-Retriever/
├── backend/                       # FastAPI backend
│   ├── main.py                    # Application entry
│   ├── requirements.txt           # Python dependencies
│   ├── app/
│   │   ├── api/                   # API routes
│   │   ├── core/                  # Configuration
│   │   ├── db/                    # Database models
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   └── services/              # Business logic
│   │       ├── embedding_service.py
│   │       ├── agent_service.py
│   │       ├── memory_graph_service.py
│   │       └── gcs_service.py
│   └── README.md                  # Backend guide
│
├── frontend/                      # React frontend
│   ├── client/                    # React app
│   │   ├── pages/                 # Route components
│   │   ├── components/            # UI components
│   │   ├── hooks/                 # Custom hooks
│   │   └── App.tsx                # App entry
│   ├── shared/                    # Shared types
│   ├── package.json               # Node dependencies
│   └── vite.config.ts             # Vite configuration
│
├── evaluate_bm25.py               # BM25 baseline evaluation
└── README.md                      # This file
```

## Quick Start

### Run Application

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to use the application.

## Evaluation

### BM25 Baseline

Evaluate traditional BM25 retrieval as a baseline:

```bash
python evaluate_bm25.py --data-path data/queries.json
```

**Metrics:**
- MRR (Mean Reciprocal Rank)
- Recall@K (K=1, 5, 10)
- MAP (Mean Average Precision)
- NDCG@K (Normalized Discounted Cumulative Gain)

### Model Evaluation

The training script automatically evaluates on the dev set:
- Development set evaluation every 0.2 epochs
- Best model saved based on MRR
- Detailed metrics logged to console and WandB

## Team

**Team Members:** Long Nguyen, Tu Nguyen, Huy Hieu, Tri Bui

**Affiliation:** Gstar Bootcamp – NTI Global Talent Program 2025

Thanks to the Gstar Bootcamp for an incredible 3 months of learning, mentorship, and support.

## License

This project is developed as part of the NTI Global Talent Program 2025 educational initiative.

## Acknowledgments

- **MSMARCO Dataset**: Microsoft Machine Reading Comprehension dataset
- **Vertex AI**: Google Cloud's AI platform
- **ZEP**: Memory infrastructure for AI applications
- **Graphiti**: Knowledge graph system
- **ColBERT**: Inspiration for multi-vector late interaction
- **BGE-M3**: Semantic embedding model for hard negatives
