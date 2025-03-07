from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    UserID = Column(Integer, primary_key=True, index=True)
    Username = Column(String(50), unique=True, index=True, nullable=False)
    Email = Column(String(100), unique=True, index=True, nullable=False)
    Password_hash = Column(String(255), nullable=False)
    Created_at = Column(DateTime, default=datetime.utcnow)

# Ensure you import this file in your database setup to create tables
