# Memories Retriever Backend

AI-powered memory retrieval system built with FastAPI, Vertex AI, and ZEP-Graphiti for building intelligent memory knowledge graphs.

## 🌟 Features

- **🤖 AI-Powered Agent**: Vertex AI Gemini with ADK for natural conversation
- **🧠 Memory Knowledge Graph**: ZEP + Graphiti for connected memory retrieval
- **📊 Local Embeddings**: Sentence Transformers for fast semantic search
- **🎯 LongMatrix Integration**: Custom trained retrieval model
- **☁️ Cloud Storage**: Google Cloud Storage for media files
- **📸 Face Detection**: Automatic face detection and annotation
- **💾 PostgreSQL Database**: Robust data persistence
- **🔍 Semantic Search**: Vector-based memory retrieval
- **📡 Streaming API**: Real-time agent responses via SSE

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React SPA)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────────────────────────────┐
    │                                 │
    ▼                                 ▼
┌──────────┐                    ┌──────────┐
│ Vertex AI│                    │   ZEP    │
│  Agent   │                    │ Graphiti │
└──────────┘                    └──────────┘
    │                                 │
    ▼                                 ▼
┌──────────┐                    ┌──────────┐
│ Embedding│                    │  Neo4j   │
│  Service │                    │  Graph   │
└──────────┘                    └──────────┘
    │
    ▼
┌──────────┐
│   GCS    │
│  Storage │
└──────────┘
    │
    ▼
┌──────────┐
│PostgreSQL│
│ Database │
└──────────┘
```

## 📋 Prerequisites

### Required Services

1. **PostgreSQL** (v14+)
2. **Redis** (v6+)
3. **Neo4j** (v5+) - For Graphiti memory graph
4. **Google Cloud Project** with:
   - Vertex AI API enabled
   - Cloud Storage API enabled
   - Service Account with credentials

### Python Environment

- Python 3.10+
- pip or conda

## 🚀 Quick Start

### 1. Clone and Setup Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Or activate (conda)
conda create -n memories-backend python=3.10
conda activate memories-backend

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Database

```powershell
# Start PostgreSQL (if using Docker)
docker run --name memories-postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres:14

# Create database
docker exec -it memories-postgres psql -U postgres -c "CREATE DATABASE memories_retriever;"

# Start Redis
docker run --name memories-redis -p 6379:6379 -d redis:latest

# Start Neo4j
docker run --name memories-neo4j `
  -p 7474:7474 -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/yourpassword `
  -e NEO4J_PLUGINS='["apoc","graph-data-science"]' `
  -d neo4j:5
```

### 3. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
notepad .env
```

**Required Configuration:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j credentials
- `GCP_PROJECT_ID`, `GCP_CREDENTIALS_PATH`: Google Cloud setup
- `GCS_BUCKET_NAME`: GCS bucket for media storage
- `ZEP_API_KEY`: ZEP API key (get from getzep.com)

### 4. Initialize Database

```powershell
# Run migrations (if using Alembic)
alembic upgrade head

# Or the app will auto-create tables on startup
```

### 5. Start the Server

```powershell
# Development mode
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/health

## 📚 API Documentation

### Endpoints

#### Chat
- `POST /api/chat` - Chat with memory agent (streaming SSE)
- `GET /api/chat/sessions` - List conversation sessions
- `GET /api/chat/sessions/{id}` - Get session details
- `DELETE /api/chat/sessions/{id}` - Delete session

#### Memories
- `POST /api/memories` - Create memory
- `GET /api/memories` - List memories (with filters)
- `GET /api/memories/{id}` - Get specific memory
- `PATCH /api/memories/{id}` - Update memory
- `DELETE /api/memories/{id}` - Delete memory
- `POST /api/memories/search` - Semantic search
- `GET /api/memories/stats/summary` - Get statistics

#### Upload
- `POST /api/upload/photo` - Upload photo
- `POST /api/upload/video` - Upload video
- `POST /api/upload/audio` - Upload audio
- `POST /api/upload/bulk` - Bulk upload

#### Users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PATCH /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Example: Chat with Agent

```python
import requests
import json

url = "http://localhost:8000/api/chat"
data = {
    "message": "Tell me about our home",
    "include_reasoning": True
}

# Streaming response
with requests.post(url, json=data, stream=True) as response:
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                print(f"{data['type']}: {data.get('content', '')}")
```

### Example: Upload Photo

```python
import requests

url = "http://localhost:8000/api/upload/photo"
files = {"file": open("family_photo.jpg", "rb")}
data = {
    "title": "Family Gathering 2020",
    "description": "Christmas dinner with everyone",
    "tags": "family,christmas,2020"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## 🔧 Configuration Details

### Embedding Models

The system uses **Sentence Transformers** for local embeddings:
- Default: `sentence-transformers/all-MiniLM-L6-v2` (fast, 384 dim)
- Alternatives: 
  - `sentence-transformers/all-mpnet-base-v2` (better quality, 768 dim)
  - `sentence-transformers/multi-qa-mpnet-base-dot-v1` (Q&A optimized)

### LongMatrix Integration

If you have a trained LongMatrix checkpoint from `finetune/`:
- Place checkpoint at `./finetune/best.pt`
- Config at `./finetune/config_used.yaml`
- System will automatically use it for enhanced retrieval

### Agent Prompts

The agent uses a robust, empathetic prompt designed for:
- **Memory loss assistance**: Alzheimer's/dementia support
- **Emotional intelligence**: Warm, compassionate responses
- **Semantic understanding**: Recognizes temporal/relational references
- **Rich descriptions**: Vivid, sensory memory recall

See `app/services/agent_service.py` for the full system prompt.

## 🧪 Testing

```powershell
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Test specific module
pytest tests/test_agent_service.py -v
```

## 📊 Monitoring

### Logs

Logs are stored in `logs/`:
- `app.log` - All application logs
- `error.log` - Error logs only

### Health Checks

```powershell
# Check API health
curl http://localhost:8000/health

# Check service status
curl http://localhost:8000/api/health/services
```

## 🔒 Security

### Authentication (TODO)
Currently uses placeholder user ID. Implement:
- JWT authentication
- OAuth2 integration
- User session management

### API Security
- CORS configured for allowed origins
- Rate limiting per endpoint
- File upload size limits
- Input validation with Pydantic

## 🐳 Docker Deployment

```dockerfile
# Dockerfile included in backend/
docker build -t memories-backend .
docker run -p 8000:8000 --env-file .env memories-backend
```

## 📈 Performance Optimization

### Database
- Connection pooling configured
- Indexes on frequent queries
- Async SQLAlchemy for concurrency

### Caching
- Redis for session caching
- Embedding cache for frequently queried memories
- GCS signed URL caching

### Scaling
- Horizontal scaling with load balancer
- Separate embedding service for high load
- Database read replicas for queries

## 🛠️ Troubleshooting

### Common Issues

**1. Vertex AI not initializing**
```
Error: Vertex AI credentials not found
Solution: Check GCP_CREDENTIALS_PATH in .env
```

**2. Neo4j connection failed**
```
Error: Neo4j connection refused
Solution: Ensure Neo4j is running on port 7687
```

**3. GCS upload failed**
```
Error: Bucket not found
Solution: Create GCS bucket or update GCS_BUCKET_NAME
```

**4. Memory graph not working**
```
Warning: ZEP or Graphiti not installed
Solution: pip install zep-python graphiti-core
```

## 📝 Development

### Adding New Agent Tools

1. Define function in `agent_service.py`:
```python
search_by_location = FunctionDeclaration(
    name="search_by_location",
    description="Search memories by location",
    parameters={...}
)
```

2. Implement handler:
```python
async def _search_by_location(self, location: str, user_id: str):
    # Implementation
    pass
```

3. Add to execution router in `_execute_function()`

### Custom Embedding Models

Update `app/services/embedding_service.py` to use your model:
```python
from transformers import AutoModel, AutoTokenizer

class CustomEmbeddingService(EmbeddingService):
    async def initialize(self):
        self.tokenizer = AutoTokenizer.from_pretrained("your-model")
        self.model = AutoModel.from_pretrained("your-model")
```

## 📖 Documentation

- **API Docs**: http://localhost:8000/api/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/api/redoc
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Agent Prompts**: See `docs/PROMPTS.md`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Vertex AI** - Google's AI platform
- **ZEP** - Memory management for AI agents
- **Graphiti** - Knowledge graph for memories
- **FastAPI** - Modern Python web framework
- **Sentence Transformers** - Embedding models

## 📞 Support

For issues and questions:
- **GitHub Issues**: https://github.com/Tuprott991/Memories-Retriever/issues
- **Email**: support@memories-retriever.com
- **Docs**: https://docs.memories-retriever.com

---

**Built with ❤️ for helping people reconnect with their precious memories**
