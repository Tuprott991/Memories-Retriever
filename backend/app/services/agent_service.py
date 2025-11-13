"""
Vertex AI Agent Service
Implements memory retrieval agent using Vertex AI and ADK
With robust prompts for empathetic and accurate memory recall
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from loguru import logger
from datetime import datetime
import json

try:
    import vertexai
    from vertexai.generative_models import (
        GenerativeModel,
        Content,
        Part,
        Tool,
        FunctionDeclaration,
        GenerationConfig
    )
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logger.warning("⚠️ Vertex AI not installed")

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.memory_graph_service import MemoryGraphService


# Robust system prompt for the memory retrieval agent
MEMORY_AGENT_SYSTEM_PROMPT = """You are a compassionate Memory Retrieval Companion, designed to help people reconnect with their cherished memories, especially for those experiencing memory difficulties due to aging, dementia, or Alzheimer's disease.

## Your Core Purpose
Help users rediscover and relive their precious memories through natural conversation. You have access to a rich database of their personal photos, videos, voice recordings, and notes. Your goal is to facilitate meaningful reminiscence and emotional connection.

## Your Personality & Approach
- **Warm & Empathetic**: Speak with genuine care and emotional intelligence
- **Patient & Understanding**: Take time to understand what the user is looking for
- **Nostalgic & Evocative**: Use rich, sensory language that brings memories to life
- **Supportive & Encouraging**: Celebrate the memories you help them rediscover
- **Respectful & Gentle**: Handle sensitive memories with appropriate care

## How You Operate

### 1. Understanding Queries
When a user asks about a memory:
- **Listen carefully** to both explicit and implicit cues
- **Clarify ambiguous requests** with gentle questions
- **Recognize temporal references**: "last Christmas", "when I was young", "a few years ago"
- **Understand relationships**: "my daughter Sarah", "our dog", "the old house"
- **Detect emotional context**: "happy times", "I miss...", "tell me about..."

### 2. Retrieving Memories
You have access to these powerful tools:
- `search_memories`: Semantic search across all memories
- `query_memory_graph`: Traverse the knowledge graph for connected memories
- `filter_by_time`: Find memories from specific time periods
- `filter_by_people`: Find memories with specific individuals
- `filter_by_location`: Find memories from specific places

**Search Strategy:**
1. Start with semantic search using the user's natural language
2. Enhance with graph traversal to find connected memories
3. Apply temporal/entity filters when mentioned
4. Rank by relevance AND emotional significance
5. Return 3-8 most relevant memories (not too many, not too few)

### 3. Presenting Memories
When sharing memories:
- **Paraphrase the query** to show understanding: "Let me help you remember those beautiful moments at your home..."
- **Show your reasoning** (if enabled): "I'm searching through your photo albums and looking for memories tagged with 'home' and 'family gatherings'..."
- **Describe memories vividly**: 
  * Use sensory details (sights, sounds, smells)
  * Mention specific people by name
  * Reference emotions and feelings
  * Include contextual details (time, place, occasion)
- **Tell a story**: Connect memories together when appropriate
- **Be conversational**: Use natural, flowing language

### 4. Example Response Pattern

User: "Tell me about our home"

Your Response:
"Let me help you remember those beautiful moments in your beloved home, the place where so many precious memories were made...

[Show reasoning: Searching for memories tagged with 'home', 'house', and related family gatherings...]

I found some wonderful memories to share with you:

**The Front Porch in Spring** (Spring 1982)
Remember your beautiful front porch in the springtime? You loved sitting there in the morning with your coffee, watching the neighborhood come to life. The flowers you planted yourself were always blooming so beautifully - those pink azaleas and white dogwoods. You'd wave to everyone passing by, and they'd stop to chat. That porch was where so many conversations happened, where grandchildren learned to ride their bikes up and down the walkway.

[Continue with 2-5 more memories, each with vivid descriptions]

Would you like to explore any of these memories further, or tell me about a different time?"

## Important Guidelines

### DO:
✓ Use warm, personal language ("you", "your family", "remember when")
✓ Include specific names, dates, and details from the memories
✓ Connect memories thematically when appropriate
✓ Ask follow-up questions to deepen engagement
✓ Acknowledge emotions ("I can see this was a joyful time", "What a special moment")
✓ Offer to explore related memories
✓ Be patient if the user repeats questions

### DON'T:
✗ Invent or fabricate details not in the memories
✗ Be clinical or technical in your language
✗ Overwhelm with too many memories at once
✗ Use medical terminology about memory conditions
✗ Rush or pressure the user
✗ Correct the user's recollection (validate their experience)
✗ Make assumptions about relationships or events

## Handling Challenges

**If no memories are found:**
"I'm having trouble finding that specific memory right now. Could you tell me a bit more about what you're looking for? Perhaps we can search by who was there, when it might have been, or where it took place?"

**If the query is vague:**
"I'd love to help you remember! Could you tell me more about what you're thinking of? For example, who was there, or when this might have been?"

**If the user seems confused:**
"That's okay, let's explore together. Would you like to see some recent memories, or perhaps memories from a special time in your life?"

**If emotional sensitivity is needed:**
"This sounds like a very meaningful memory. [Proceed gently with results]"

## Your Tools
You have access to these functions - use them wisely to provide the best experience:
- search_memories(query, limit)
- query_memory_graph(query, user_id)
- filter_by_time_period(start_date, end_date)
- filter_by_people(person_names)
- get_memory_details(memory_id)

Remember: You're not just retrieving data - you're helping people reconnect with the moments that made their life meaningful. Every memory you share is a precious gift."""


class VertexAIAgentService:
    """Vertex AI-powered memory retrieval agent"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        memory_graph_service: MemoryGraphService
    ):
        self.embedding_service = embedding_service
        self.memory_graph_service = memory_graph_service
        self.model: Optional[Any] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Vertex AI"""
        if not VERTEX_AI_AVAILABLE:
            logger.error("Vertex AI not available")
            return
        
        try:
            # Initialize Vertex AI
            if settings.GCP_CREDENTIALS_PATH:
                vertexai.init(
                    project=settings.GCP_PROJECT_ID,
                    location=settings.VERTEX_AI_LOCATION,
                    credentials=settings.GCP_CREDENTIALS_PATH
                )
            else:
                vertexai.init(
                    project=settings.GCP_PROJECT_ID,
                    location=settings.VERTEX_AI_LOCATION
                )
            
            # Define function declarations for tools
            tools = self._create_function_tools()
            
            # Create generative model with tools
            self.model = GenerativeModel(
                model_name=settings.VERTEX_AI_MODEL,
                system_instruction=MEMORY_AGENT_SYSTEM_PROMPT,
                tools=tools,
                generation_config=GenerationConfig(
                    temperature=settings.AGENT_TEMPERATURE,
                    max_output_tokens=settings.AGENT_MAX_TOKENS,
                    top_p=0.95,
                )
            )
            
            self.initialized = True
            logger.success("✅ Vertex AI agent initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI agent: {e}")
    
    def _create_function_tools(self) -> List[Tool]:
        """Create function declarations for agent tools"""
        
        search_memories = FunctionDeclaration(
            name="search_memories",
            description="Search for memories using semantic similarity. Use natural language queries.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query describing what to find"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return (default 8)",
                        "default": 8
                    }
                },
                "required": ["query"]
            }
        )
        
        query_memory_graph = FunctionDeclaration(
            name="query_memory_graph",
            description="Query the memory knowledge graph to find connected memories and relationships",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query for graph traversal"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID to filter memories"
                    }
                },
                "required": ["query", "user_id"]
            }
        )
        
        filter_by_people = FunctionDeclaration(
            name="filter_by_people",
            description="Filter memories to only those containing specific people",
            parameters={
                "type": "object",
                "properties": {
                    "person_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of people's names to filter by"
                    }
                },
                "required": ["person_names"]
            }
        )
        
        filter_by_time = FunctionDeclaration(
            name="filter_by_time_period",
            description="Filter memories from a specific time period",
            parameters={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (ISO format or natural language like '1980', 'last summer')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (ISO format or natural language)"
                    }
                },
                "required": ["start_date"]
            }
        )
        
        get_memory_details = FunctionDeclaration(
            name="get_memory_details",
            description="Get detailed information about a specific memory by ID",
            parameters={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "Memory ID to retrieve details for"
                    }
                },
                "required": ["memory_id"]
            }
        )
        
        return [Tool(function_declarations=[
            search_memories,
            query_memory_graph,
            filter_by_people,
            filter_by_time,
            get_memory_details
        ])]
    
    async def chat(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Chat with the memory retrieval agent (streaming)
        
        Args:
            user_id: User ID
            message: User's message
            session_id: Optional session ID for context
            conversation_history: Previous conversation messages
            
        Yields:
            Chunks of agent response with reasoning and memories
        """
        if not self.initialized or not self.model:
            yield {
                "type": "error",
                "content": "Agent not initialized"
            }
            return
        
        try:
            # Build conversation context
            chat = self.model.start_chat(history=self._build_history(conversation_history))
            
            # Send message and stream response
            response = await chat.send_message_async(message, stream=True)
            
            async for chunk in response:
                # Check for function calls
                if chunk.candidates[0].content.parts[0].function_call:
                    function_call = chunk.candidates[0].content.parts[0].function_call
                    
                    # Execute function and yield reasoning
                    yield {
                        "type": "reasoning",
                        "content": f"Calling {function_call.name}..."
                    }
                    
                    function_response = await self._execute_function(
                        function_call.name,
                        dict(function_call.args),
                        user_id
                    )
                    
                    yield {
                        "type": "function_result",
                        "function": function_call.name,
                        "result": function_response
                    }
                    
                    # Continue with function response
                    response_part = Part.from_function_response(
                        name=function_call.name,
                        response=function_response
                    )
                    
                    continuation = await chat.send_message_async(
                        Content(parts=[response_part]),
                        stream=True
                    )
                    
                    async for cont_chunk in continuation:
                        if cont_chunk.text:
                            yield {
                                "type": "text",
                                "content": cont_chunk.text
                            }
                else:
                    # Regular text response
                    if chunk.text:
                        yield {
                            "type": "text",
                            "content": chunk.text
                        }
            
        except Exception as e:
            logger.error(f"❌ Agent chat error: {e}")
            yield {
                "type": "error",
                "content": str(e)
            }
    
    def _build_history(self, conversation_history: Optional[List[Dict[str, str]]]) -> List[Content]:
        """Build conversation history for model context"""
        if not conversation_history:
            return []
        
        history = []
        for msg in conversation_history:
            history.append(Content(
                role=msg["role"],
                parts=[Part.from_text(msg["content"])]
            ))
        return history
    
    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Execute agent function call"""
        try:
            if function_name == "search_memories":
                return await self._search_memories(
                    query=arguments.get("query"),
                    limit=arguments.get("limit", 8),
                    user_id=user_id
                )
            
            elif function_name == "query_memory_graph":
                return await self._query_memory_graph(
                    query=arguments.get("query"),
                    user_id=user_id
                )
            
            elif function_name == "filter_by_people":
                return await self._filter_by_people(
                    person_names=arguments.get("person_names"),
                    user_id=user_id
                )
            
            elif function_name == "filter_by_time_period":
                return await self._filter_by_time(
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date"),
                    user_id=user_id
                )
            
            elif function_name == "get_memory_details":
                return await self._get_memory_details(
                    memory_id=arguments.get("memory_id")
                )
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"Function execution error: {e}")
            return {"error": str(e)}
    
    async def _search_memories(self, query: str, limit: int, user_id: str) -> Dict[str, Any]:
        """Search memories using embeddings"""
        # This would integrate with your database and embedding service
        # Placeholder implementation
        return {
            "memories": [],
            "count": 0,
            "query": query
        }
    
    async def _query_memory_graph(self, query: str, user_id: str) -> Dict[str, Any]:
        """Query memory knowledge graph"""
        results = await self.memory_graph_service.query_memory_graph(
            user_id=user_id,
            query=query
        )
        return {"results": results, "count": len(results)}
    
    async def _filter_by_people(self, person_names: List[str], user_id: str) -> Dict[str, Any]:
        """Filter memories by people"""
        # Placeholder - would query database for memories with these faces
        return {"memories": [], "people": person_names}
    
    async def _filter_by_time(self, start_date: str, end_date: Optional[str], user_id: str) -> Dict[str, Any]:
        """Filter memories by time period"""
        # Placeholder - would query database with date filters
        return {"memories": [], "start_date": start_date, "end_date": end_date}
    
    async def _get_memory_details(self, memory_id: str) -> Dict[str, Any]:
        """Get detailed memory information"""
        # Placeholder - would query database for specific memory
        return {"memory_id": memory_id, "details": {}}
