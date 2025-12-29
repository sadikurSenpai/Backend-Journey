from sqlmodel import SQLModel, create_engine, Session, text
from typing import Generator
import logging

logger = logging.getLogger(__name__)

POSTGRES_CONNECTION_STRING = "postgresql+psycopg2://postgres:Sheam000@localhost:5432/auth"

engine = create_engine(
    POSTGRES_CONNECTION_STRING,
    pool_pre_ping=True,  # Validates connections before using them
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL query logging
)

def create_db_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        return False

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def check_database_connection() -> bool:
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False