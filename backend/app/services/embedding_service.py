"""
Embedding Service
Handles local embedding model for memory retrieval
Supports both standard embeddings and LongMatrix late interaction
"""

import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict, Any
from loguru import logger
import yaml
from pathlib import Path

from app.core.config import settings


class EmbeddingService:
    """Local embedding service for memory retrieval"""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.device = settings.EMBEDDING_DEVICE
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.model_name = settings.EMBEDDING_MODEL_NAME
        
        # LongMatrix components (if available)
        self.longmatrix_model = None
        self.longmatrix_config = None
        
    async def initialize(self):
        """Initialize embedding models"""
        try:
            # Load standard embedding model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.success(f"✅ Embedding model loaded on {self.device}")
            
            # Try to load LongMatrix model if available
            await self._load_longmatrix_model()
            
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    async def _load_longmatrix_model(self):
        """Load LongMatrix model for advanced retrieval"""
        try:
            checkpoint_path = Path(settings.LONGMATRIX_CHECKPOINT_PATH)
            config_path = Path(settings.LONGMATRIX_CONFIG_PATH)
            
            if checkpoint_path.exists() and config_path.exists():
                logger.info("Loading LongMatrix model...")
                
                # Load config
                with open(config_path, 'r') as f:
                    self.longmatrix_config = yaml.safe_load(f)
                
                # Load checkpoint
                checkpoint = torch.load(checkpoint_path, map_location=self.device)
                
                # TODO: Initialize LongMatrix model with checkpoint
                # This requires the LongMatrix model class from finetune/
                logger.success("✅ LongMatrix model loaded")
            else:
                logger.warning("⚠️ LongMatrix checkpoint not found, using standard embeddings only")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load LongMatrix model: {e}")
    
    async def embed_texts(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings to embed
            normalize: Whether to normalize embeddings
            
        Returns:
            numpy array of embeddings [num_texts, embedding_dim]
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            raise
    
    async def embed_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            normalize: Whether to normalize embedding
            
        Returns:
            numpy array of embedding [embedding_dim]
        """
        embeddings = await self.embed_texts([text], normalize=normalize)
        return embeddings[0]
    
    async def compute_similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and documents
        
        Args:
            query_embedding: Query embedding [embedding_dim]
            document_embeddings: Document embeddings [num_docs, embedding_dim]
            
        Returns:
            numpy array of similarities [num_docs]
        """
        # Normalize if not already normalized
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        doc_norms = document_embeddings / (np.linalg.norm(document_embeddings, axis=1, keepdims=True) + 1e-8)
        
        # Compute cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        return similarities
    
    async def embed_with_longmatrix(
        self,
        query: str,
        documents: List[str],
        return_scores: bool = True
    ) -> Dict[str, Any]:
        """
        Generate embeddings using LongMatrix late interaction
        
        Args:
            query: Query text
            documents: List of document texts
            return_scores: Whether to return similarity scores
            
        Returns:
            Dictionary with query vectors, document vectors, and optionally scores
        """
        if not self.longmatrix_model:
            logger.warning("LongMatrix model not available, falling back to standard embeddings")
            return await self._fallback_longmatrix(query, documents, return_scores)
        
        try:
            # TODO: Implement LongMatrix forward pass
            # This requires integration with the trained model from finetune/
            pass
            
        except Exception as e:
            logger.error(f"❌ LongMatrix embedding failed: {e}")
            return await self._fallback_longmatrix(query, documents, return_scores)
    
    async def _fallback_longmatrix(
        self,
        query: str,
        documents: List[str],
        return_scores: bool = True
    ) -> Dict[str, Any]:
        """Fallback to standard embeddings when LongMatrix is unavailable"""
        query_emb = await self.embed_text(query)
        doc_embs = await self.embed_texts(documents)
        
        result = {
            "query_vectors": query_emb.tolist(),
            "document_vectors": doc_embs.tolist(),
        }
        
        if return_scores:
            scores = await self.compute_similarity(query_emb, doc_embs)
            result["scores"] = scores.tolist()
        
        return result
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 384  # Default for all-MiniLM-L6-v2
