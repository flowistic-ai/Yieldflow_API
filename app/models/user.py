from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.database import BaseModel


class User(BaseModel):
    """User model for authentication and account management"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    plan = Column(String(50), default="free", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")


class APIKey(BaseModel):
    """API key model for API authentication"""
    
    __tablename__ = "api_keys"
    
    key_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)  # User-friendly name for the key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    allowed_ips = Column(Text, nullable=True)  # JSON string of allowed IP addresses
    scopes = Column(Text, nullable=True)  # JSON string of allowed scopes/features
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    usage_records = relationship("UsageRecord", back_populates="api_key", cascade="all, delete-orphan")


class UsageRecord(BaseModel):
    """Usage tracking for rate limiting and analytics"""
    
    __tablename__ = "usage_records"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="usage_records")
    api_key = relationship("APIKey", back_populates="usage_records")
