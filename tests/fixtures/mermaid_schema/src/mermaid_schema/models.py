from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
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


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("blog.posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("blog.tags.id"), primary_key=True),
    schema="blog",
)


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    posts = relationship("Post", back_populates="author")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    comments = relationship("Comment", back_populates="user")


class UserProfile(Base):
    """Extended user profile information."""

    __tablename__ = "user_profiles"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("public.users.id"), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    bio = Column(Text)

    # Relationships
    user = relationship("User", back_populates="profile")


class Post(Base):
    """Blog post model."""

    __tablename__ = "posts"
    __table_args__ = {"schema": "blog"}

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    is_published = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("public.users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")


class Comment(Base):
    """Comments on posts."""

    __tablename__ = "comments"
    __table_args__ = {"schema": "blog"}

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("blog.posts.id"))
    user_id = Column(Integer, ForeignKey("public.users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Tag(Base):
    """Tags for posts."""

    __tablename__ = "tags"
    __table_args__ = {"schema": "blog"}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    posts = relationship("Post", secondary=post_tags, back_populates="tags")


class PageView(Base):
    """Tracks page views for posts."""

    __tablename__ = "page_views"
    __table_args__ = {"schema": "analytics"}

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("blog.posts.id"))
    viewed_at = Column(DateTime, default=datetime.utcnow)
    viewer_ip = Column(String(45))

    # Relationships
    post = relationship("Post")
