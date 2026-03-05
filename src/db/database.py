from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import settings

engine = create_engine(
    str(settings.DATABASE_URL),
    # Maintain 20 persistent connections in the pool
    pool_size=20, 
    # If the 20 are busy, allow up to 10 more temporary overflow connections
    max_overflow=10, 
    # If all 30 are busy, make user wait up to 30 seconds for a connection to free up before throwing a 500
    pool_timeout=30, 
    # Heartbeat check to prevent disconnected idle sessions
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()