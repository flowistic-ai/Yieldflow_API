from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )


class BaseModel(Base, TimestampMixin):
    """Base model with common fields"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
