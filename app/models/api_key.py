from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

Base = declarative_base()

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, index=True)
    description = Column(String(256), nullable=True)
    user_id = Column(Integer, nullable=True, index=True)  # 可选，支持多用户
    expires_at = Column(DateTime, nullable=True)           # 新增：过期时间
    is_active = Column(Boolean, default=True, nullable=False)  # 新增：是否有效
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 