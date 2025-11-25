# LongMatrix Memories Retriever

A complete end-to-end system for personal memory retrieval using a custom-trained neural retrieval model. This project demonstrates the full machine learning pipeline from model architecture design, large-scale pre-training on MSMARCO, synthetic data generation, domain-specific finetuning, to production deployment in a real-world application.

## Table of Contents

- [Overview](#overview)
- [Model Architecture](#model-architecture)
- [Training Pipeline](#training-pipeline)
- [Synthetic Data Generation](#synthetic-data-generation)
- [Domain Finetuning](#domain-finetuning)
- [Memories Retrieval Application](#memories-retrieval-application)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Team](#team)

## Overview

This project implements a complete retrieval system for personal memories (photos, videos, audio) using natural language queries. The core innovation is the **LongMatrix** architecture - a lightweight neural retrieval model that combines lexical matching with semantic understanding through a unique multi-vector late interaction mechanism.

**Key Highlights:**

- Custom neural architecture optimized for retrieval tasks
- Large-scale pre-training on MSMARCO v2.1 (500K+ query-document pairs)
- Multi-GPU distributed training with PyTorch DDP
- Automated synthetic data generation using Vertex AI Gemini-2.5-Pro
- Domain-specific finetuning on memory retrieval data
- Production-ready FastAPI backend with Vertex AI agents and ZEP-Graphiti knowledge graphs
- Modern React frontend with streaming AI chat interface

## Model Architecture

### LongMatrix: Multi-Vector Retrieval with Late Interaction

The LongMatrix model is a lightweight neural retrieval architecture inspired by ColBERT but optimized for efficiency and adaptability.

#### Architecture Components

**1. Lexical Encoder**
```
Input Text → Tokenization → Embedding Layer (d_lex_emb=512)
           ↓
   Layer Normalization
           ↓
   Multi-Head Self-Attention (8 heads)
      - Supports Flash Attention 2
      - SDPA (Scaled Dot-Product Attention)
      - Fallback to standard attention
           ↓
   Attention Pooling → Token Representations (d_lex=192)
```

**2. Low-Rank Projection**
```
Token Vectors (d_lex=192) → Low-Rank Factorization (rank=256)
                          ↓
                    U (rank × d_lex)  ×  V (rank × m_teacher)
                          ↓
                Final Embeddings (m_teacher=768)
                          ↓
                   L2 Normalization
```

**3. Late Interaction Scoring**

For single-vector mode (documents):
```
similarity(query, doc) = mean(query_vectors) · doc_vector
```

For multi-vector mode (queries):
```
similarity(query, doc) = mean_i(max_j(q_i · d_j))
```
Where:
- q_i are the top-K query token vectors (K=4)
- d_j are document token vectors (typically K=1 for efficiency)

#### Key Features

- **Multi-Vector Representation**: Queries use 4 token vectors for nuanced matching
- **Single-Vector Documents**: Documents compressed to 1 vector for fast retrieval
- **Flash Attention Support**: Optional Flash Attention 2 for 2-3x speedup
- **Gradient Checkpointing**: Enables training with larger batch sizes
- **Orthogonal Regularization**: Ensures diverse learned representations
- **Mixed Precision Training**: BF16/FP16 support for faster training

#### Model Hyperparameters

```yaml
d_lex_emb: 512      # Embedding dimension
d_lex: 192          # Lexical representation dimension
rank: 256           # Low-rank projection dimension
heads: 8            # Number of attention heads
topk_q: 4           # Query token vectors to keep
topk_d: 1           # Document token vectors to keep
m_teacher: 768      # Final embedding dimension
```

#### Loss Functions

The model is trained with a composite loss:

1. **Retrieval Loss (λ_ret=1.0)**: InfoNCE contrastive loss
2. **Lexical Loss (λ_lex=0.25)**: Term matching similarity
3. **Entropy Regularization (λ_ent=0.0015)**: Prevents attention collapse
4. **Orthogonality Loss (λ_ortho=0.001)**: Promotes diverse representations
5. **Knowledge Distillation (optional)**: Learns from teacher models like BGE-M3

## Training Pipeline

### Phase 1: Pre-training on MSMARCO v2.1

The model is pre-trained on the MSMARCO v2.1 passage ranking dataset, containing millions of real web search queries.

#### Dataset

- **Source**: HuggingFace `unicamp-dl/mmarco`
- **Split**: Train (500K+ samples), Validation (6,980 samples)
- **Task**: Retrieve relevant passages for search queries

#### Hard Negatives Mining

Three strategies for mining challenging negative examples:

1. **BM25 (Lexical)**: Uses Pyserini/Lucene or rank-bm25
   - Fast lexical matching
   - Finds documents with overlapping terms but different semantics

2. **BGE-M3 (Semantic)**: Uses sentence-transformers + FAISS
   - Semantic similarity search
   - Finds documents with similar embeddings but different meanings

3. **Combo**: Combines BM25 + BGE-M3
   - 3 BM25 negatives + 4 M3 negatives per query
   - Best of both lexical and semantic hard negatives

#### Distributed Training

Multi-GPU training using PyTorch DDP (Distributed Data Parallel):

```bash
torchrun --nproc_per_node=4 --master_port=29500 \
  finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --max_train_rows 500000 \
  --neg_method combo \
  --k_neg_bm25 3 \
  --k_neg_m3 4 \
  --batch_size 32 \
  --accum_steps 2 \
  --epochs 3 \
  --lr 2e-4 \
  --output_dir runs/msmarco_ddp
```

**Training Configuration:**

- **Hardware**: 4x A100 GPUs (80GB)
- **Effective Batch Size**: 2,048 (32 × 2 × 4)
- **Mixed Precision**: BF16
- **Gradient Accumulation**: 2 steps
- **Learning Rate**: 2e-4 with cosine schedule
- **Warmup**: 1,500 steps
- **Epochs**: 3-20 depending on convergence

**Performance:**

- Single GPU: ~500 samples/sec, ~60 min/epoch
- 4 GPUs (DDP): ~1,800 samples/sec, ~17 min/epoch (3.6x speedup)
- Total training time: 5-20 hours depending on dataset size

#### Training Features

- **Exponential Moving Average (EMA)**: Stabilizes training
- **Gradient Clipping**: Prevents exploding gradients
- **Early Stopping**: Based on validation MRR
- **WandB Integration**: Experiment tracking and visualization
- **Automatic Checkpointing**: Best model saved based on dev performance

## Synthetic Data Generation

To adapt the model to personal memory retrieval, we generate domain-specific training data using LLM-based synthesis.

### System Architecture

```
Vertex AI Gemini-2.5-Pro
         ↓
Batch Generation (10-20 records/call)
         ↓
Memory Captions + Natural Queries + Hard Negatives
         ↓
Output: queries.json (5,000+ records)
```

### Data Format

Each generated record contains:

```json
{
  "id": "memory_0001",
  "caption": "Leo's 1st birthday party at Grandma's house, April 2023, with family and friends celebrating",
  "queries": [
    "Show me Leo's first birthday party",
    "Pictures of Leo turning one",
    "When we celebrated at Grandma's house",
    "Leo's birthday with the family",
    "April 2023 birthday celebration"
  ],
  "negatives": [
    "Leo's second birthday party at home",
    "Christmas celebration at Grandma's 2022",
    "Family gathering for Thanksgiving"
  ]
}
```

### Generation Process

1. **Caption Creation**: LLM generates diverse memory descriptions
   - Family events, vacations, milestones, everyday moments
   - Specific names, dates, locations, emotions
   - Varying formality and detail levels

2. **Query Paraphrasing**: 5-10 natural language variations
   - Different perspectives ("my son", "our dog")
   - Temporal references ("last summer", "two years ago")
   - Emotional cues ("I miss", "we had fun")

3. **Hard Negatives**: 2-3 confusable alternatives
   - Similar subjects or events
   - Overlapping details
   - Useful for contrastive learning

### Usage

```bash
# Generate 5000 memory records
python synthetic_data_genration/data_generator.py \
  --num_records 5000 \
  --output_path data/queries.json \
  --batch_size 10
```

**Performance:**
- Batch size: 10 records per API call
- Generation rate: ~200-300 records/minute
- Cost-efficient with batching
- Scales to 10,000+ records

### Diversity Coverage

The LLM is instructed to create diverse memories covering:

- **Event Types**: Birthdays, graduations, weddings, vacations, holidays, daily life
- **Subjects**: Named family members, friends, pets, groups
- **Locations**: Home rooms, outdoor venues, cities, countries, landmarks
- **Timeframes**: Specific dates, seasons, years, relative times
- **Emotions**: Celebratory, nostalgic, casual, formal

## Domain Finetuning

After pre-training on MSMARCO, the model is fine-tuned on the synthetic memory retrieval dataset.

### Data Conversion

Convert JSON to TSV format for training:

```bash
python finetune/data_converter.py \
  --input data/queries.json \
  --output_dir data/processed \
  --dev_ratio 0.02
```

Output:
- `data/processed/train.tsv`: Training samples (98%)
- `data/processed/dev.tsv`: Validation samples (2%)

### Training Configuration

```yaml
# finetune/config_memories.yaml
train_tsv: data/processed/train.tsv
dev_tsv: data/processed/dev.tsv
output_dir: runs/memories_retriever

# Resume from MSMARCO checkpoint
resume: finetune/longmatrix.pt

# Model architecture
d_lex_emb: 512
d_lex: 192
rank: 256
heads: 8
late_interaction: true
topk_q: 4
topk_d: 1

# Training hyperparameters
epochs: 20
batch_size: 448
accum_steps: 8
lr: 0.005
warmup_steps: 1500
max_len: 512

# Loss weights
lambda_ret: 1.0
lambda_lex: 0.25
lambda_ent: 0.0015
lambda_ortho: 0.001

# Optimization
dtype: bf16
grad_ckpt: true
allow_tf32: true
attn_backend: sdpa
```

### Training Execution

```bash
# Single GPU training
python finetune/train_longmatrix.py --config finetune/config_memories.yaml

# Multi-GPU training (4 GPUs)
torchrun --nproc_per_node=4 --master_port=29500 \
  finetune/train_longmatrix.py \
  --config finetune/config_memories.yaml --ddp
```

### Training Metrics

- **MRR (Mean Reciprocal Rank)**: Primary metric
- **Recall@K**: Proportion of queries with relevant doc in top-K
- **Precision@K**: Relevant documents found / K
- **NDCG@K**: Ranking quality metric
- **Loss Components**: Retrieval, lexical, entropy, orthogonality

### Model Export

After training, export the model for deployment:

```yaml
export_after_train: true
export_out_dir: models/memories_retriever
export_demo_query: "Show me photos of Leo's first birthday"
export_demo_topk: 5
```

This creates a deployable model checkpoint optimized for inference.

## Memories Retrieval Application

A production-ready web application demonstrating the trained model in action.

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
│  LongMatrix  │          │    Neo4j     │
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

1. **LongMatrix Integration**
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
   - Results ranked by LongMatrix model
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
pnpm install
pnpm dev
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
├── finetune/                      # Model training code
│   ├── train_longmatrix.py        # Main training script
│   ├── train_longmatrix_update.py # MSMARCO training script
│   ├── data.py                    # Hard negatives mining
│   ├── config_memories.yaml       # Memory finetuning config
│   ├── ddp_4gpu_allmini.yaml      # Multi-GPU config
│   ├── launch_ddp.ps1             # DDP launcher script
│   ├── data_converter.py          # JSON → TSV converter
│   ├── verify_checkpoint.py       # Model verification
│   ├── MSMARCO_TRAINING_GUIDE.md  # MSMARCO training guide
│   └── DDP_TRAINING_GUIDE.md      # Distributed training guide
│
├── synthetic_data_genration/      # Data generation
│   ├── data_generator.py          # Main generation script
│   ├── config.py                  # Configuration
│   ├── README.md                  # Usage guide
│   └── SYSTEM_OVERVIEW.md         # System architecture
│
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
├── data/                          # Training data
│   ├── queries.json               # Generated memory data
│   └── processed/
│       ├── train.tsv              # Training TSV
│       └── dev.tsv                # Validation TSV
│
├── evaluate_bm25.py               # BM25 baseline evaluation
├── BM25_EVALUATION.md             # Evaluation guide
├── TRAINING_GUIDE.md              # Training guide
├── INTEGRATION_GUIDE.md           # Integration guide
└── README.md                      # This file
```

## Quick Start

### 1. Generate Synthetic Data

```bash
python synthetic_data_genration/data_generator.py \
  --num_records 5000 \
  --output_path data/queries.json
```

### 2. Convert to Training Format

```bash
python finetune/data_converter.py \
  --input data/queries.json \
  --output_dir data/processed
```

### 3. Train Model (Optional: Pre-train on MSMARCO)

```bash
# Pre-training on MSMARCO
torchrun --nproc_per_node=4 --master_port=29500 \
  finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --max_train_rows 500000 \
  --neg_method combo \
  --batch_size 32 \
  --accum_steps 2 \
  --epochs 3
```

### 4. Finetune on Memory Data

```bash
# Single GPU
python finetune/train_longmatrix.py --config finetune/config_memories.yaml

# Multi-GPU (4 GPUs)
torchrun --nproc_per_node=4 \
  finetune/train_longmatrix.py \
  --config finetune/config_memories.yaml --ddp
```

### 5. Run Application

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
pnpm install
pnpm dev
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