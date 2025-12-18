"""
Unit tests for A2A Well-Known Manifest helpers
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock


class TestFetchManifest:
    """Tests for manifest fetching functions."""
    
    def test_fetch_manifest_sync_success(self):
        """Test successful synchronous manifest fetch."""
        from amorce.well_known import fetch_manifest_sync
        
        mock_manifest = {
            "name": "Test Agent",
            "url": "https://test.com",
            "protocol_version": "A2A/1.0",
            "authentication": {"type": "amorce", "public_key": "test-key"}
        }
        
        with patch('amorce.well_known.httpx.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_manifest
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            result = fetch_manifest_sync("test-agent-id")
            
            assert result == mock_manifest
            assert result["protocol_version"] == "A2A/1.0"
            mock_get.assert_called_once()
    
    def test_fetch_manifest_sync_not_found(self):
        """Test 404 error handling."""
        from amorce.well_known import fetch_manifest_sync
        import httpx
        
        with patch('amorce.well_known.httpx.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
            )
            mock_get.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                fetch_manifest_sync("nonexistent-agent")
    
    @pytest.mark.asyncio
    async def test_fetch_manifest_async_success(self):
        """Test async manifest fetch."""
        from amorce.well_known import fetch_manifest
        
        mock_manifest = {
            "name": "Async Agent",
            "protocol_version": "A2A/1.0"
        }
        
        with patch('amorce.well_known.httpx.AsyncClient') as MockClient:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = mock_manifest
            mock_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await fetch_manifest("async-agent-id")
            
            assert result == mock_manifest


class TestServeWellKnown:
    """Tests for framework-specific middleware."""
    
    def test_serve_well_known_auto_detect_fastapi(self):
        """Test auto-detection of FastAPI framework."""
        from amorce.well_known import serve_well_known
        
        # Create mock FastAPI app
        mock_app = MagicMock()
        mock_app.__class__.__name__ = "FastAPI"
        
        with patch('amorce.well_known.serve_well_known_fastapi') as mock_fastapi:
            mock_fastapi.return_value = mock_app
            result = serve_well_known(mock_app, agent_id="test-id")
            mock_fastapi.assert_called_once()
    
    def test_serve_well_known_auto_detect_flask(self):
        """Test auto-detection of Flask framework."""
        from amorce.well_known import serve_well_known
        
        mock_app = MagicMock()
        mock_app.__class__.__name__ = "Flask"
        
        with patch('amorce.well_known.serve_well_known_flask') as mock_flask:
            mock_flask.return_value = mock_app
            result = serve_well_known(mock_app, agent_id="test-id")
            mock_flask.assert_called_once()
    
    def test_serve_well_known_unknown_framework(self):
        """Test error on unknown framework."""
        from amorce.well_known import serve_well_known
        
        mock_app = MagicMock()
        mock_app.__class__.__name__ = "UnknownFramework"
        
        with pytest.raises(ValueError, match="Could not auto-detect framework"):
            serve_well_known(mock_app, agent_id="test-id")
    
    def test_serve_well_known_explicit_framework(self):
        """Test explicit framework specification."""
        from amorce.well_known import serve_well_known
        
        mock_app = MagicMock()
        
        with patch('amorce.well_known.serve_well_known_flask') as mock_flask:
            mock_flask.return_value = mock_app
            serve_well_known(mock_app, agent_id="test-id", framework="flask")
            mock_flask.assert_called_once()


class TestGenerateManifestFile:
    """Tests for static manifest file generation."""
    
    def test_generate_manifest_file(self, tmp_path):
        """Test manifest file generation."""
        from amorce.well_known import generate_manifest_file
        
        mock_manifest = {
            "name": "Static Agent",
            "protocol_version": "A2A/1.0"
        }
        
        output_path = str(tmp_path / ".well-known" / "agent.json")
        
        with patch('amorce.well_known.fetch_manifest_sync') as mock_fetch:
            mock_fetch.return_value = mock_manifest
            
            result = generate_manifest_file("test-agent", output_path)
            
            assert result == output_path
            
            # Verify file was created
            with open(output_path) as f:
                saved_manifest = json.load(f)
            
            assert saved_manifest == mock_manifest
            assert saved_manifest["protocol_version"] == "A2A/1.0"


class TestIntegration:
    """Integration tests with real API (optional, run with --integration flag)."""
    
    @pytest.mark.integration
    def test_real_manifest_fetch(self):
        """Test fetching a real manifest from production API."""
        from amorce.well_known import fetch_manifest_sync
        
        # Use a known agent ID from production
        manifest = fetch_manifest_sync("0b631b00-6668-42c1-a0af-2c8cf565d7f2")
        
        assert "name" in manifest
        assert "protocol_version" in manifest
        assert manifest["protocol_version"] == "A2A/1.0"
        assert "authentication" in manifest
        assert manifest["authentication"]["type"] == "amorce"
