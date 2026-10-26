"""
Shared test fixtures.

Uses SQLite in-memory via aiosqlite so no external Postgres is required.
We override BOTH `get_db` AND `get_db_session` (the alias in dependencies.py).
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db
from app.core import dependencies as deps_module

# ---------------------------------------------------------------------------
# In-memory SQLite engine
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def _override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    # Make sure all models are imported so metadata knows about them
    import app.organizations.models  # noqa: F401
    import app.users.models  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    """HTTP client wired to the FastAPI app with SQLite test DB."""
    # Override all DB dependencies
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[deps_module.get_db_session] = _override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
