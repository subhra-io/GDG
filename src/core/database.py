"""Database connection management for PostgreSQL, MongoDB, and Redis."""

from typing import Optional
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from src.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# SQLAlchemy Base for ORM models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections for PostgreSQL, MongoDB, and Redis."""
    
    def __init__(self):
        """Initialize database manager."""
        self._postgres_engine: Optional[create_engine] = None
        self._postgres_session_factory: Optional[sessionmaker] = None
        self._mongo_client: Optional[MongoClient] = None
        self._mongo_db: Optional[MongoDatabase] = None
        self._redis_client: Optional[Redis] = None
        self._async_redis_client: Optional[AsyncRedis] = None
    
    def initialize_postgres(self) -> None:
        """Initialize PostgreSQL connection pool."""
        try:
            logger.info(
                "Initializing PostgreSQL connection",
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db
            )
            
            self._postgres_engine = create_engine(
                settings.postgres_url,
                poolclass=pool.QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
            
            self._postgres_session_factory = sessionmaker(
                bind=self._postgres_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # Test connection
            from sqlalchemy import text
            with self._postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("PostgreSQL connection initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize PostgreSQL connection", error=str(e))
            raise
    
    def initialize_mongodb(self) -> None:
        """Initialize MongoDB connection."""
        try:
            logger.info(
                "Initializing MongoDB connection",
                host=settings.mongodb_host,
                port=settings.mongodb_port,
                database=settings.mongodb_db
            )
            
            self._mongo_client = MongoClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            self._mongo_db = self._mongo_client[settings.mongodb_db]
            
            # Test connection
            self._mongo_client.server_info()
            
            logger.info("MongoDB connection initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize MongoDB connection", error=str(e))
            raise
    
    def initialize_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            logger.info(
                "Initializing Redis connection",
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db
            )
            
            self._redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self._redis_client.ping()
            
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Redis connection", error=str(e))
            raise
    
    def get_postgres_session(self) -> Session:
        """Get PostgreSQL session."""
        if not self._postgres_session_factory:
            raise RuntimeError("PostgreSQL not initialized. Call initialize_postgres() first.")
        return self._postgres_session_factory()
    
    @asynccontextmanager
    async def postgres_session_context(self):
        """Context manager for PostgreSQL session."""
        session = self.get_postgres_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_mongodb(self) -> MongoDatabase:
        """Get MongoDB database instance."""
        if not self._mongo_db:
            raise RuntimeError("MongoDB not initialized. Call initialize_mongodb() first.")
        return self._mongo_db
    
    def get_redis(self) -> Redis:
        """Get Redis client instance."""
        if not self._redis_client:
            raise RuntimeError("Redis not initialized. Call initialize_redis() first.")
        return self._redis_client
    
    def close_all(self) -> None:
        """Close all database connections."""
        logger.info("Closing all database connections")
        
        if self._postgres_engine:
            self._postgres_engine.dispose()
            logger.info("PostgreSQL connection closed")
        
        if self._mongo_client:
            self._mongo_client.close()
            logger.info("MongoDB connection closed")
        
        if self._redis_client:
            self._redis_client.close()
            logger.info("Redis connection closed")


# Global database manager instance
db_manager = DatabaseManager()
