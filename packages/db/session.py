"""Database session management and configuration."""

import os
import ssl
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from .models import Base

# Load environment variables from .env file
load_dotenv()

# Database URL configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SSLMODE = os.getenv("DATABASE_SSLMODE")  # e.g. 'require', 'verify-full'
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "true").lower() == "true"

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in your .env file or environment."
    )

# If DATABASE_SSLMODE is provided and not present in the URL, append/override it.
def _apply_sslmode_to_url(url: str, sslmode: str | None) -> str:
    if not sslmode:
        return url
    parts = urlsplit(url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))
    query_params["sslmode"] = sslmode
    new_query = urlencode(query_params)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

DATABASE_URL = _apply_sslmode_to_url(DATABASE_URL, DATABASE_SSLMODE)

# Determine if SSL is required based on URL or env
def _is_ssl_required(url: str, sslmode_env: str | None) -> bool:
    parts = urlsplit(url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))
    sslmode = (sslmode_env or query_params.get("sslmode") or "").lower()
    return sslmode in {"require", "verify-ca", "verify-full"}

# Async database URL (for async operations)
def _build_async_url_without_sslmode(url: str) -> str:
    parts = urlsplit(url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))
    # Remove sslmode for asyncpg (it doesn't accept this kw)
    if "sslmode" in query_params:
        del query_params["sslmode"]
    new_query = urlencode(query_params)
    async_scheme = "postgresql+asyncpg" if parts.scheme.startswith("postgresql") else parts.scheme
    return urlunsplit((async_scheme, parts.netloc, parts.path, new_query, parts.fragment))

ASYNC_DATABASE_URL = _build_async_url_without_sslmode(DATABASE_URL)

# Create engines
engine = create_engine(DATABASE_URL, echo=DATABASE_ECHO)

# For asyncpg, when SSL is required, provide an SSLContext that uses system CAs
async_connect_args = {}
if _is_ssl_required(DATABASE_URL, DATABASE_SSLMODE):
    ssl_context = ssl.create_default_context()
    ca_bundle_path = os.getenv("RDS_CA_BUNDLE", "/etc/ssl/certs/aws-rds-global-bundle.pem")
    try:
        if ca_bundle_path and os.path.exists(ca_bundle_path):
            ssl_context.load_verify_locations(cafile=ca_bundle_path)
    except Exception:
        # Fallback to system default CAs if custom bundle load fails
        ssl_context = ssl.create_default_context()
    async_connect_args = {"ssl": ssl_context}

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=DATABASE_ECHO,
    connect_args=async_connect_args
)

# Create session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get synchronous database session.
    Use this for non-async operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get asynchronous database session.
    Use this for async operations (recommended).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# For Streamlit or other sync contexts
def get_sync_session() -> Session:
    """Get a synchronous session for Streamlit or other sync contexts."""
    return SessionLocal()