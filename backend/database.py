from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase_config import supabase
import os
from dotenv import load_dotenv

load_dotenv()

# Use Supabase PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(DATABASE_URL)

# SessionLocal is our database session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase():
    """Get Supabase client"""
    return supabase
