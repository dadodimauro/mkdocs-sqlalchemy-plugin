"""Test SQLAlchemy models for the plugin."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class."""

    metadata = MetaData(naming_convention=convention)


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"
    __table_args__ = {"schema": "profiles"}

    id = Column(Integer, primary_key=True, doc="Unique user identifier")
    username = Column(String(50), unique=True, nullable=False, doc="User's login name")
    email = Column(String(120), unique=True, nullable=False, doc="User's email address")
    is_active = Column(Boolean, default=True, doc="Whether the user account is active")
    created_at = Column(
        DateTime, default=datetime.utcnow, doc="When the user was created"
    )

    # Relationships
    posts = relationship("blog.posts", back_populates="author")
    profile = relationship(
        "profiles.user_profiles", back_populates="user", uselist=False
    )


class Post(Base):
    """Blog post model."""

    __tablename__ = "posts"
    __table_args__ = {"schema": "blog"}

    id = Column(Integer, primary_key=True, doc="Unique post identifier")
    title = Column(String(200), nullable=False, doc="Post title")
    content = Column(Text, doc="Post content")
    is_published = Column(Boolean, default=False, doc="Whether the post is published")
    user_id = Column(Integer, ForeignKey("profiles.users.id"), doc="Author's user ID")
    created_at = Column(
        DateTime, default=datetime.utcnow, doc="When the post was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="When the post was last updated",
        index=True,
    )

    # Relationships
    author = relationship("profiles.users", back_populates="posts")


class UserProfile(Base):
    """Extended user profile information."""

    __tablename__ = "user_profiles"
    __table_args__ = {"schema": "profiles"}

    id = Column(Integer, primary_key=True, doc="Unique profile identifier")
    user_id = Column(
        Integer, ForeignKey("profiles.users.id"), unique=True, doc="Associated user ID"
    )
    first_name = Column(String(50), doc="User's first name")
    last_name = Column(String(50), doc="User's last name")
    bio = Column(Text, doc="User's biography")

    # Relationships
    user = relationship("profiles.users", back_populates="profile")
