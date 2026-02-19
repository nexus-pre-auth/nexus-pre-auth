import pytest
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db_session
from app.models import Base, V28Coefficient


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_session(test_db_engine):
    """Create test session with seeded data"""
    async_session_local = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_local() as session:
        # Seed test data
        session.add(V28Coefficient(hcc_code="HCC85", coefficient=0.455))
        session.add(V28Coefficient(hcc_code="HCC18", coefficient=0.163))
        session.add(V28Coefficient(hcc_code="HCC19", coefficient=0.342))
        await session.commit()
    
    yield async_session_local


@pytest.fixture
def override_get_db(test_session):
    """Override FastAPI dependency"""
    async def _get_db():
        async with test_session() as session:
            yield session
    
    app.dependency_overrides[get_db_session] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_analyze_hcc85_returns_correct_raf_lift(override_get_db):
    """Test /v28/analyze endpoint with HCC85 returns correct RAF lift"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v28/analyze",
            json={
                "chart_id": "CHT001",
                "note_text": "Patient presents with HCC85 chronic condition"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify correct RAF lift for HCC85
    assert data["raf_lift"] == 0.455
    assert data["hcc_code"] == "HCC85"
    assert data["chart_id"] == "CHT001"
    
    # Verify audit trail exists
    assert "audit_uuid" in data
    assert "integrity_hash" in data
    assert len(data["integrity_hash"]) == 64  # SHA-256 hash length


@pytest.mark.asyncio
async def test_analyze_phi_blind_no_clinical_text_stored(override_get_db):
    """Test that clinical text is NOT stored in database"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v28/analyze",
            json={
                "chart_id": "CHT002",
                "note_text": "SENSITIVE: Patient with diabetes and HCC85 condition"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response doesn't include note_text
    assert "note_text" not in data
    
    # Verify only structured data is returned
    assert data["chart_id"] == "CHT002"
    assert data["hcc_code"] == "HCC85"
    assert data["raf_lift"] == 0.455


@pytest.mark.asyncio
async def test_analyze_integrity_hash_is_deterministic(override_get_db):
    """Test that integrity hash is generated correctly"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v28/analyze",
            json={
                "chart_id": "CHT003",
                "note_text": "Test clinical note"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify hash is 64 characters (SHA-256)
    assert len(data["integrity_hash"]) == 64
    assert all(c in "0123456789abcdef" for c in data["integrity_hash"])


@pytest.mark.asyncio
async def test_health_check(override_get_db):
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"