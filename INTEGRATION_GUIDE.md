# Backend Integration Guide

This guide explains how the Memories Retriever backend integrates with the frontend and all its components.

## 🎯 Overview

The backend provides a robust API for:
1. **Memory Management** - Upload, store, retrieve memories
2. **AI Agent Chat** - Natural conversation for memory retrieval
3. **Knowledge Graph** - Connected memory exploration via ZEP-Graphiti
4. **Semantic Search** - Vector-based memory search
5. **Media Storage** - GCS-based photo/video/audio storage

## 📡 API Integration

### Frontend to Backend Connection

Update your frontend's `shared/api.ts` to connect to the backend:

```typescript
// frontend/shared/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
  // Chat endpoints
  async chat(message: string, sessionId?: string) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    return response; // Returns streaming SSE response
  },

  // Memory endpoints
  async searchMemories(query: string, limit: number = 10) {
    const response = await fetch(`${API_BASE_URL}/memories/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit })
    });
    return response.json();
  },

  async uploadPhoto(file: File, title: string, description: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);

    const response = await fetch(`${API_BASE_URL}/upload/photo`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }
};
```

### Streaming Chat Integration

Replace the mock data in `MemoryPalace.tsx`:

```typescript
// frontend/client/pages/MemoryPalace.tsx
const handleSendMessage = async (e: React.FormEvent, journeyPrompt?: string) => {
  e.preventDefault();
  const messageContent = journeyPrompt || input.trim();
  if (!messageContent || loading) return;

  setInput("");
  setMessages((prev) => [...prev, { role: "user", content: messageContent }]);
  setLoading(true);

  try {
    // Call backend streaming API
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: messageContent,
        include_reasoning: true
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let assistantMessage = '';
    let memories = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          const parsed = JSON.parse(data);

          if (parsed.type === 'reasoning') {
            setReasoningModal({
              visible: true,
              reasoning: parsed.content,
              paraphrasedQuery: messageContent
            });
          } else if (parsed.type === 'text') {
            assistantMessage += parsed.content;
          } else if (parsed.type === 'function_result') {
            if (parsed.result.memories) {
              memories = parsed.result.memories;
            }
          }
        }
      }
    }

    setReasoningModal(null);
    setLoading(false);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: assistantMessage,
        memories: memories
      }
    ]);

  } catch (error) {
    console.error('Chat error:', error);
    setLoading(false);
  }
};
```

### File Upload Integration

Replace localStorage-based uploads in `FamilyHub.tsx`:

```typescript
// frontend/client/pages/FamilyHub.tsx
const handleFileUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', uploadFormData.title);
  formData.append('description', uploadFormData.description);

  try {
    const response = await fetch('http://localhost:8000/api/upload/photo', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    
    // Update UI with uploaded memory
    setMemoryMetadata(prev => [...prev, {
      id: result.memory_id,
      type: 'photo',
      title: uploadFormData.title,
      description: uploadFormData.description,
      timestamp: new Date().toISOString()
    }]);

    setSaveNotification('✅ Photo uploaded successfully!');
  } catch (error) {
    console.error('Upload error:', error);
    setSaveNotification('❌ Upload failed');
  }
};
```

## 🔧 Configuration

### Environment Variables

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

### CORS Setup

The backend is already configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:8080` (Alternative port)

To add more origins, update `backend/.env`:

```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:8080","https://yourdomain.com"]
```

## 🚀 Running Full Stack

### Terminal 1: Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

Backend runs on: `http://localhost:8000`

### Terminal 2: Frontend

```powershell
cd frontend
pnpm dev
```

Frontend runs on: `http://localhost:5173`

### Terminal 3: Services (Docker)

```powershell
# PostgreSQL
docker run --name memories-postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres:14

# Redis
docker run --name memories-redis -p 6379:6379 -d redis:latest

# Neo4j
docker run --name memories-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/yourpassword -d neo4j:5
```

## 📊 Data Flow

### Memory Upload Flow

```
User uploads photo in FamilyHub
         ↓
Frontend sends FormData to /api/upload/photo
         ↓
Backend validates file
         ↓
Upload to GCS
         ↓
Create Memory record in PostgreSQL
         ↓
Generate embedding for description
         ↓
Add to memory graph (Graphiti)
         ↓
Return memory_id and media_url
         ↓
Frontend updates UI
```

### Chat Flow

```
User sends message in MemoryPalace
         ↓
Frontend posts to /api/chat
         ↓
Backend streams response (SSE)
         ↓
Agent analyzes query
         ↓
Calls tools (search_memories, query_memory_graph)
         ↓
Retrieves relevant memories from database
         ↓
Generates empathetic response
         ↓
Streams back to frontend
         ↓
Frontend displays reasoning + memories
```

## 🎨 Response Formats

### Memory Object

```typescript
interface Memory {
  id: string;
  user_id: string;
  type: "photo" | "video" | "voice" | "note";
  title: string;
  description: string;
  media_url: string;
  thumbnail_url?: string;
  timestamp?: string;
  created_at: string;
  tags: string[];
  faces: Face[];
}
```

### Chat Response (Streaming)

```typescript
// Reasoning chunk
{
  "type": "reasoning",
  "content": "Searching for memories about home..."
}

// Text chunk
{
  "type": "text",
  "content": "I found some beautiful memories..."
}

// Function result
{
  "type": "function_result",
  "function": "search_memories",
  "result": {
    "memories": [...],
    "count": 5
  }
}
```

## 🔐 Authentication (Future)

To add authentication:

1. **Backend**: Implement JWT in `app/core/auth.py`
2. **Frontend**: Add auth context and token management
3. **API calls**: Include `Authorization: Bearer <token>` header

Example:

```typescript
// frontend/lib/auth.ts
export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token');
  
  return fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
}
```

## 🐛 Debugging

### Check Backend Health

```powershell
curl http://localhost:8000/health
```

### View Backend Logs

```powershell
Get-Content backend/logs/app.log -Wait
```

### Test API Endpoints

```powershell
# Search memories
curl -X POST http://localhost:8000/api/memories/search `
  -H "Content-Type: application/json" `
  -d '{"query": "family gathering", "limit": 5}'

# Upload photo
curl -X POST http://localhost:8000/api/upload/photo `
  -F "file=@photo.jpg" `
  -F "title=Test Photo" `
  -F "description=A test upload"
```

## 📈 Performance Tips

1. **Caching**: Backend uses Redis for session caching
2. **Pagination**: Use `skip` and `limit` parameters for large lists
3. **Streaming**: Chat uses SSE for real-time responses
4. **Lazy Loading**: Load images on-demand using signed URLs
5. **Batch Operations**: Use bulk upload for multiple files

## 🎯 Next Steps

1. **Replace Mock Data**: Remove `mockMemories.ts` and use real API
2. **Add Authentication**: Implement user auth flow
3. **Face Detection**: Connect face detection to backend
4. **Real-time Updates**: Add WebSocket for live memory updates
5. **Offline Support**: Add service worker for offline access

## 📚 Additional Resources

- **API Docs**: http://localhost:8000/api/docs
- **Backend README**: `backend/README.md`
- **Agent Prompts**: `backend/app/services/agent_service.py`
- **Database Schema**: `backend/app/models/`

---

**Questions?** Check the backend logs or API documentation!
