"""
db.py helps connecting to database
"""
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv()

db_url = os.getenv("DATABASE_URL")

# Construct connection string
SQLALCHEMY_DATABASE_URL = db_url


# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session local class for handling database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a base class for models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
