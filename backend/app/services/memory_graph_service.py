"""
Memory Graph Service
Integrates ZEP and Graphiti for building and querying memory knowledge graphs
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import asyncio

try:
    from zep_python import ZepClient, Message, Memory
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeNode, EntityNode
    from neo4j import AsyncGraphDatabase
    ZEP_AVAILABLE = True
except ImportError:
    ZEP_AVAILABLE = False
    logger.warning("⚠️ ZEP or Graphiti not installed, memory graph features will be limited")

from app.core.config import settings


class MemoryGraphService:
    """Service for managing memory knowledge graphs with ZEP and Graphiti"""
    
    def __init__(self):
        self.zep_client: Optional[Any] = None
        self.graphiti: Optional[Any] = None
        self.neo4j_driver: Optional[Any] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize ZEP and Graphiti connections"""
        try:
            if not ZEP_AVAILABLE:
                logger.warning("⚠️ Memory graph service running in limited mode")
                self.initialized = True
                return
            
            # Initialize ZEP client
            logger.info("Initializing ZEP client...")
            self.zep_client = ZepClient(
                api_key=settings.ZEP_API_KEY,
                api_url=settings.ZEP_API_URL
            )
            
            # Initialize Neo4j driver for Graphiti
            logger.info("Initializing Neo4j connection for Graphiti...")
            self.neo4j_driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            
            # Verify Neo4j connection
            await self._verify_neo4j_connection()
            
            # Initialize Graphiti
            logger.info("Initializing Graphiti...")
            self.graphiti = Graphiti(
                uri=settings.NEO4J_URI,
                user=settings.NEO4J_USER,
                password=settings.NEO4J_PASSWORD,
                database=settings.NEO4J_DATABASE
            )
            
            await self.graphiti.initialize()
            
            self.initialized = True
            logger.success("✅ Memory graph service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory graph service: {e}")
            # Continue with limited functionality
            self.initialized = True
    
    async def _verify_neo4j_connection(self):
        """Verify Neo4j connection"""
        try:
            async with self.neo4j_driver.session() as session:
                result = await session.run("RETURN 1 as num")
                record = await result.single()
                if record["num"] == 1:
                    logger.success("✅ Neo4j connection verified")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        if self.graphiti:
            await self.graphiti.close()
    
    async def add_memory_to_graph(
        self,
        user_id: str,
        memory_id: str,
        memory_type: str,
        title: str,
        description: str,
        timestamp: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        faces: Optional[List[Dict[str, str]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a memory to the knowledge graph
        
        Args:
            user_id: User ID
            memory_id: Memory ID
            memory_type: Type of memory (photo, video, voice, note)
            title: Memory title
            description: Memory description
            timestamp: When the memory occurred
            tags: User-defined tags
            faces: Detected faces with names
            metadata: Additional metadata
            
        Returns:
            Dictionary with graph node IDs and relationships
        """
        if not self.initialized or not self.graphiti:
            logger.warning("Memory graph not available, skipping graph addition")
            return {}
        
        try:
            # Create episode node for this memory
            episode_text = f"{title}. {description}"
            if faces:
                people = [f["name"] for f in faces if f.get("name")]
                if people:
                    episode_text += f" People: {', '.join(people)}."
            
            # Add episode to Graphiti
            episode = await self.graphiti.add_episode(
                name=title,
                episode_body=episode_text,
                source_description=f"Memory {memory_type}",
                reference_time=timestamp or datetime.utcnow(),
                metadata={
                    "memory_id": memory_id,
                    "user_id": user_id,
                    "memory_type": memory_type,
                    "tags": tags or [],
                    **(metadata or {})
                }
            )
            
            # Extract entities (people, places, etc.) and relationships
            entities = await self._extract_entities_from_memory(
                title, description, faces, metadata
            )
            
            logger.info(f"✅ Added memory {memory_id} to knowledge graph")
            
            return {
                "episode_id": str(episode.uuid) if episode else None,
                "entities": entities
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add memory to graph: {e}")
            return {}
    
    async def _extract_entities_from_memory(
        self,
        title: str,
        description: str,
        faces: Optional[List[Dict[str, str]]],
        metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract entities from memory content"""
        entities = []
        
        # Extract people from faces
        if faces:
            for face in faces:
                if face.get("name"):
                    entities.append({
                        "type": "person",
                        "name": face["name"],
                        "description": face.get("description", "")
                    })
        
        # Extract location from metadata
        if metadata and metadata.get("location"):
            entities.append({
                "type": "location",
                "name": metadata["location"],
                "description": ""
            })
        
        return entities
    
    async def query_memory_graph(
        self,
        user_id: str,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query the memory knowledge graph
        
        Args:
            user_id: User ID
            query: Natural language query
            max_results: Maximum number of results
            
        Returns:
            List of relevant memory episodes with context
        """
        if not self.initialized or not self.graphiti:
            logger.warning("Memory graph not available for querying")
            return []
        
        try:
            # Search for relevant episodes in the graph
            results = await self.graphiti.search(
                query=query,
                num_results=max_results,
                metadata_filter={"user_id": user_id}
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "episode_id": str(result.uuid),
                    "memory_id": result.metadata.get("memory_id"),
                    "name": result.name,
                    "content": result.content,
                    "score": result.score if hasattr(result, "score") else 0.0,
                    "timestamp": result.created_at,
                    "entities": result.metadata.get("entities", []),
                    "metadata": result.metadata
                })
            
            logger.info(f"✅ Found {len(formatted_results)} results in memory graph")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Failed to query memory graph: {e}")
            return []
    
    async def add_conversation_to_zep(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add conversation exchange to ZEP for memory tracking
        
        Args:
            session_id: ZEP session ID
            user_message: User's message
            assistant_message: Assistant's response
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if not self.zep_client:
            return False
        
        try:
            messages = [
                Message(
                    role="user",
                    content=user_message,
                    metadata=metadata or {}
                ),
                Message(
                    role="assistant",
                    content=assistant_message,
                    metadata=metadata or {}
                )
            ]
            
            await self.zep_client.memory.add_session(
                session_id=session_id,
                messages=messages
            )
            
            logger.info(f"✅ Added conversation to ZEP session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add conversation to ZEP: {e}")
            return False
    
    async def get_conversation_context(
        self,
        session_id: str,
        last_n: int = 10
    ) -> List[Dict[str, str]]:
        """
        Retrieve conversation context from ZEP
        
        Args:
            session_id: ZEP session ID
            last_n: Number of recent messages to retrieve
            
        Returns:
            List of messages with role and content
        """
        if not self.zep_client:
            return []
        
        try:
            memory = await self.zep_client.memory.get_session(session_id=session_id)
            
            messages = []
            for msg in memory.messages[-last_n:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at
                })
            
            return messages
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to retrieve ZEP context: {e}")
            return []
    
    async def build_memory_connections(
        self,
        user_id: str,
        memory_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Build connections between related memories in the graph
        
        Args:
            user_id: User ID
            memory_ids: List of memory IDs to connect
            
        Returns:
            Dictionary with connection statistics
        """
        if not self.initialized or not self.graphiti:
            return {"connections": 0}
        
        try:
            # Use Graphiti to find and create relationships between memories
            # This leverages Graphiti's entity extraction and relationship detection
            
            connections_created = 0
            
            # Query the graph for each memory
            for memory_id in memory_ids:
                # Find related episodes based on shared entities
                query = f"""
                MATCH (e:Episode {{memory_id: $memory_id}})
                MATCH (e)-[:HAS_ENTITY]->(entity)<-[:HAS_ENTITY]-(related:Episode)
                WHERE related.user_id = $user_id AND related.memory_id <> $memory_id
                MERGE (e)-[r:RELATED_TO]->(related)
                ON CREATE SET r.created_at = datetime()
                RETURN count(r) as connections
                """
                
                async with self.neo4j_driver.session() as session:
                    result = await session.run(
                        query,
                        memory_id=memory_id,
                        user_id=user_id
                    )
                    record = await result.single()
                    if record:
                        connections_created += record["connections"]
            
            logger.info(f"✅ Created {connections_created} memory connections")
            return {"connections": connections_created}
            
        except Exception as e:
            logger.error(f"❌ Failed to build memory connections: {e}")
            return {"connections": 0}
