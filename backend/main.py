"""
Memories Retriever Backend - Main Application Entry Point
FastAPI backend with Vertex AI, ADK agents, and ZEP-Graphiti memory graph
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.router import api_router
from app.services.embedding_service import EmbeddingService
from app.services.memory_graph_service import MemoryGraphService
from app.services.gcs_service import GCSService
from app.db.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    logger.info("🚀 Starting Memories Retriever Backend...")
    
    # Initialize database
    logger.info("Initializing database connection...")
    await init_db()
    
    # Initialize services
    logger.info("Loading embedding model...")
    embedding_service = EmbeddingService()
    await embedding_service.initialize()
    app.state.embedding_service = embedding_service
    
    logger.info("Initializing memory graph service...")
    memory_graph_service = MemoryGraphService()
    await memory_graph_service.initialize()
    app.state.memory_graph_service = memory_graph_service
    
    logger.info("Initializing GCS service...")
    gcs_service = GCSService()
    await gcs_service.initialize()
    app.state.gcs_service = gcs_service
    
    logger.success("✅ All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Memories Retriever Backend...")
    await close_db()
    await memory_graph_service.close()
    logger.success("✅ Graceful shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Memories Retriever API",
    description="AI-powered memory retrieval system with Vertex AI, ADK agents, and ZEP-Graphiti",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Setup logging
setup_logging()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}")
    
    # Log request
    logger.info(
        f"🔵 {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"✅ {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": duration
            }
        )
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - Error ({duration:.3f}s): {str(e)}",
            extra={
                "request_id": request_id,
                "error": str(e),
                "duration": duration
            }
        )
        raise


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": request.url.path
        }
    )


# Include API router
app.include_router(api_router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "memories-retriever-backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Memories Retriever API",
        "docs": "/api/docs",
        "health": "/health",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
