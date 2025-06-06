import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_AUTH_HOST", "localhost")
DB_PORT = os.getenv("DB_AUTH_PORT", "5432")
DB_NAME = os.getenv("DB_AUTH_NAME", "auth_db")
DB_USER = os.getenv("DB_AUTH_USER", "auth_user")
DB_PASSWORD = os.getenv("DB_AUTH_PASSWORD", "auth_pass")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
