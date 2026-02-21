"""Main application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.core import DatabaseManager, setup_logging, get_logger
from src.core.database import db_manager, Base
from src.routes import policy_router, violations_router, dashboard_router, data_router
from src.routes.monitoring import router as monitoring_router
from src.routes.llm import router as llm_router
from src.routes.rule_graph import router as rule_graph_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting PolicySentinel application")
    
    # Initialize database connections
    try:
        db_manager.initialize_postgres()
        db_manager.initialize_mongodb()
        db_manager.initialize_redis()
        logger.info("All database connections initialized")
        
        # Create tables
        engine = db_manager._postgres_engine
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
    except Exception as e:
        logger.error("Failed to initialize database connections", error=str(e))
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down PolicySentinel application")
    db_manager.close_all()


# Create FastAPI application
app = FastAPI(
    title="PolicySentinel",
    description="AI-Powered Compliance Monitoring Platform",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(policy_router)
app.include_router(violations_router)
app.include_router(dashboard_router)
app.include_router(data_router)
app.include_router(monitoring_router)
app.include_router(llm_router)
app.include_router(rule_graph_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "PolicySentinel",
        "version": "0.1.0",
        "status": "running",
        "description": "AI-Powered Compliance Monitoring Platform"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "postgres": "unknown",
        "mongodb": "unknown",
        "redis": "unknown"
    }
    
    # Check PostgreSQL
    try:
        from sqlalchemy import text
        session = db_manager.get_postgres_session()
        session.execute(text("SELECT 1"))
        session.close()
        health_status["postgres"] = "healthy"
    except Exception as e:
        logger.error("PostgreSQL health check failed", error=str(e))
        health_status["postgres"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check MongoDB
    try:
        mongo_db = db_manager.get_mongodb()
        mongo_db.command("ping")
        health_status["mongodb"] = "healthy"
    except Exception as e:
        logger.error("MongoDB health check failed", error=str(e))
        health_status["mongodb"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = db_manager.get_redis()
        redis_client.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        health_status["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
