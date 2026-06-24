from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
import logging

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# ==================== DATABASE ENGINE ====================

# Configurar engine con pool
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ==================== SESSION ====================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==================== DEPENDENCY ====================

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database"""
    from models import Base
    
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

# ==================== CONNECTION POOL ====================

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set connection parameters"""
    pass

@event.listens_for(engine, "pool_connect")
def receive_pool_connect(dbapi_conn, connection_record):
    """Handle pool connection"""
    logger.debug("Pool connection established")

@event.listens_for(engine, "pool_checkout")
def receive_pool_checkout(dbapi_conn, connection_record, connection_proxy):
    """Handle pool checkout"""
    pass

@event.listens_for(engine, "pool_detach")
def receive_pool_detach(dbapi_conn, connection_record):
    """Handle pool detach"""
    logger.debug("Pool connection detached")

@event.listens_for(engine, "pool_disconnect")
def receive_pool_disconnect(dbapi_conn, connection_record):
    """Handle pool disconnect"""
    logger.debug("Pool connection disconnected")

# ==================== HEALTH CHECK ====================

def check_db_connection() -> bool:
    """Check database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
