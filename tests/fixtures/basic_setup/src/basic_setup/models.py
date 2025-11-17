"""Test SQLAlchemy models for the plugin."""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class."""

    pass


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, doc="Unique user identifier")
    username = Column(String(50), unique=True, nullable=False, doc="User's login name")
    email = Column(String(120), unique=True, nullable=False, doc="User's email address")
    is_active = Column(Boolean, default=True, doc="Whether the user account is active")
    created_at = Column(
        DateTime, default=datetime.utcnow, doc="When the user was created"
    )

    # Relationships
    posts = relationship("Post", back_populates="author")
    profile = relationship("UserProfile", back_populates="user", uselist=False)


class Post(Base):
    """Blog post model."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, doc="Unique post identifier")
    title = Column(String(200), nullable=False, doc="Post title")
    content = Column(Text, doc="Post content")
    is_published = Column(Boolean, default=False, doc="Whether the post is published")
    user_id = Column(Integer, ForeignKey("users.id"), doc="Author's user ID")
    created_at = Column(
        DateTime, default=datetime.utcnow, doc="When the post was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="When the post was last updated",
    )

    # Relationships
    author = relationship("User", back_populates="posts")


class UserProfile(Base):
    """Extended user profile information."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, doc="Unique profile identifier")
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, doc="Associated user ID"
    )
    first_name = Column(String(50), doc="User's first name")
    last_name = Column(String(50), doc="User's last name")
    bio = Column(Text, doc="User's biography")

    # Relationships
    user = relationship("User", back_populates="profile")
