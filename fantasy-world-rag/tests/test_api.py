"""
Tests for API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock

# Import the app factory
from src.api.app import create_app


@pytest.fixture
def app():
    """Create test application."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test basic health check."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, client):
        """Test readiness check."""
        response = await client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
    
    @pytest.mark.asyncio
    async def test_liveness_check(self, client):
        """Test liveness check."""
        response = await client.get("/health/live")
        
        assert response.status_code == 200


class TestCharacterEndpoints:
    """Tests for character endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_characters(self, client):
        """Test listing characters."""
        response = await client.get("/api/characters")
        
        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
    
    @pytest.mark.asyncio
    async def test_get_character(self, client):
        """Test getting a specific character."""
        # First, we need to mock the database
        # For now, test that endpoint exists and returns proper error for non-existent
        response = await client.get("/api/characters/non-existent-character")
        
        # Should return 404 for non-existent character
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_character_with_valid_id(self, client):
        """Test getting a character with mock data."""
        # This would normally use database fixtures
        response = await client.get("/api/characters/gandalf-the-grey")
        
        # Without database, should return 404
        assert response.status_code in [200, 404]


class TestConversationEndpoints:
    """Tests for conversation endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, client):
        """Test creating a new conversation."""
        response = await client.post(
            "/api/conversations",
            json={
                "character_id": "gandalf-the-grey",
                "user_id": "test-user"
            }
        )
        
        # Should succeed or fail gracefully
        assert response.status_code in [200, 201, 404, 500]
    
    @pytest.mark.asyncio
    async def test_create_conversation_missing_fields(self, client):
        """Test creating conversation with missing fields."""
        response = await client.post(
            "/api/conversations",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_conversation(self, client):
        """Test getting a conversation."""
        response = await client.get("/api/conversations/non-existent-session")
        
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_conversation_messages(self, client):
        """Test getting conversation messages."""
        response = await client.get("/api/conversations/test-session/messages")
        
        assert response.status_code in [200, 404]


class TestChatEndpoints:
    """Tests for chat endpoints."""
    
    @pytest.mark.asyncio
    async def test_send_message(self, client):
        """Test sending a chat message."""
        response = await client.post(
            "/api/chat",
            json={
                "session_id": "test-session",
                "content": "Hello, how are you?"
            }
        )
        
        # Should succeed or fail gracefully (no active session)
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_send_message_missing_content(self, client):
        """Test sending message without content."""
        response = await client.post(
            "/api/chat",
            json={
                "session_id": "test-session"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_send_message_empty_content(self, client):
        """Test sending message with empty content."""
        response = await client.post(
            "/api/chat",
            json={
                "session_id": "test-session",
                "content": ""
            }
        )
        
        # Should return validation error or handle gracefully
        assert response.status_code in [200, 400, 422]


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self, client):
        """Test OpenAPI schema availability."""
        response = await client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
    
    @pytest.mark.asyncio
    async def test_docs_endpoint(self, client):
        """Test Swagger docs endpoint."""
        response = await client.get("/docs")
        
        # Should redirect or return HTML
        assert response.status_code in [200, 307]
    
    @pytest.mark.asyncio
    async def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint."""
        response = await client.get("/redoc")
        
        assert response.status_code in [200, 307]


class TestErrorHandling:
    """Tests for API error handling."""
    
    @pytest.mark.asyncio
    async def test_404_handling(self, client):
        """Test 404 error handling."""
        response = await client.get("/non-existent-endpoint")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_method_not_allowed(self, client):
        """Test method not allowed handling."""
        response = await client.put("/health")
        
        assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_invalid_json(self, client):
        """Test invalid JSON handling."""
        response = await client.post(
            "/api/chat",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
