"""
A2A Well-Known Manifest Helper

Provides easy integration for serving /.well-known/agent.json endpoints
to make your agent discoverable in the A2A ecosystem.
"""

from typing import Optional, Dict, Any, Callable
import json
import httpx


AMORCE_DIRECTORY_URL = "https://amorce-trust-api-425870997313.us-central1.run.app"


async def fetch_manifest(
    agent_id: str,
    directory_url: str = AMORCE_DIRECTORY_URL,
) -> Dict[str, Any]:
    """
    Fetch the A2A manifest for an agent from the Amorce Directory.
    
    Args:
        agent_id: Your registered agent ID
        directory_url: Amorce Directory URL (default: production)
        
    Returns:
        A2A-compatible manifest dict
    """
    url = f"{directory_url}/api/v1/agents/{agent_id}/manifest"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def fetch_manifest_sync(
    agent_id: str,
    directory_url: str = AMORCE_DIRECTORY_URL,
) -> Dict[str, Any]:
    """
    Synchronous version of fetch_manifest.
    """
    url = f"{directory_url}/api/v1/agents/{agent_id}/manifest"
    
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def serve_well_known_fastapi(
    app,
    agent_id: str,
    directory_url: str = AMORCE_DIRECTORY_URL,
    cache_ttl: int = 300,
):
    """
    Add /.well-known/agent.json route to a FastAPI app.
    
    Args:
        app: FastAPI application instance
        agent_id: Your registered agent ID
        directory_url: Amorce Directory URL
        cache_ttl: Cache duration in seconds (default: 5 minutes)
        
    Example:
        from fastapi import FastAPI
        from amorce.well_known import serve_well_known_fastapi
        
        app = FastAPI()
        serve_well_known_fastapi(app, agent_id="my-agent-id")
    """
    import time
    
    _cache: Dict[str, Any] = {"manifest": None, "fetched_at": 0}
    
    @app.get("/.well-known/agent.json")
    async def get_well_known_manifest():
        """Serve A2A manifest for agent discovery."""
        now = time.time()
        
        # Return cached if still valid
        if _cache["manifest"] and (now - _cache["fetched_at"]) < cache_ttl:
            return _cache["manifest"]
        
        # Fetch fresh manifest
        manifest = await fetch_manifest(agent_id, directory_url)
        _cache["manifest"] = manifest
        _cache["fetched_at"] = now
        
        return manifest
    
    return app


def serve_well_known_flask(
    app,
    agent_id: str,
    directory_url: str = AMORCE_DIRECTORY_URL,
    cache_ttl: int = 300,
):
    """
    Add /.well-known/agent.json route to a Flask app.
    
    Args:
        app: Flask application instance
        agent_id: Your registered agent ID
        directory_url: Amorce Directory URL
        cache_ttl: Cache duration in seconds
        
    Example:
        from flask import Flask
        from amorce.well_known import serve_well_known_flask
        
        app = Flask(__name__)
        serve_well_known_flask(app, agent_id="my-agent-id")
    """
    from flask import jsonify
    import time
    
    _cache: Dict[str, Any] = {"manifest": None, "fetched_at": 0}
    
    @app.route("/.well-known/agent.json")
    def get_well_known_manifest():
        """Serve A2A manifest for agent discovery."""
        now = time.time()
        
        # Return cached if still valid
        if _cache["manifest"] and (now - _cache["fetched_at"]) < cache_ttl:
            return jsonify(_cache["manifest"])
        
        # Fetch fresh manifest
        manifest = fetch_manifest_sync(agent_id, directory_url)
        _cache["manifest"] = manifest
        _cache["fetched_at"] = now
        
        return jsonify(manifest)
    
    return app


def serve_well_known(
    app,
    agent_id: str,
    framework: str = "auto",
    directory_url: str = AMORCE_DIRECTORY_URL,
    cache_ttl: int = 300,
):
    """
    Universal helper to serve /.well-known/agent.json.
    
    Automatically detects FastAPI vs Flask framework.
    
    Args:
        app: Your web application instance
        agent_id: Your registered agent ID
        framework: "fastapi", "flask", or "auto" (auto-detect)
        directory_url: Amorce Directory URL
        cache_ttl: Cache duration in seconds
        
    Returns:
        The app instance with the route added
        
    Example:
        from amorce.well_known import serve_well_known
        
        # FastAPI
        app = serve_well_known(app, agent_id="my-agent-id")
        
        # Flask
        app = serve_well_known(app, agent_id="my-agent-id", framework="flask")
    """
    if framework == "auto":
        # Auto-detect framework
        class_name = app.__class__.__name__
        if class_name == "FastAPI":
            framework = "fastapi"
        elif class_name == "Flask":
            framework = "flask"
        else:
            raise ValueError(
                f"Could not auto-detect framework for {class_name}. "
                "Please specify framework='fastapi' or framework='flask'"
            )
    
    if framework == "fastapi":
        return serve_well_known_fastapi(app, agent_id, directory_url, cache_ttl)
    elif framework == "flask":
        return serve_well_known_flask(app, agent_id, directory_url, cache_ttl)
    else:
        raise ValueError(f"Unsupported framework: {framework}")


def generate_manifest_file(
    agent_id: str,
    output_path: str = ".well-known/agent.json",
    directory_url: str = AMORCE_DIRECTORY_URL,
) -> str:
    """
    Generate a static manifest file that can be deployed with your agent.
    
    Args:
        agent_id: Your registered agent ID
        output_path: Path to write the manifest file
        directory_url: Amorce Directory URL
        
    Returns:
        Path to the generated file
        
    Example:
        from amorce.well_known import generate_manifest_file
        
        # Generate for deployment
        generate_manifest_file("my-agent-id", ".well-known/agent.json")
    """
    import os
    
    manifest = fetch_manifest_sync(agent_id, directory_url)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Generated {output_path}")
    print(f"   Host this file at: https://your-agent.com/.well-known/agent.json")
    
    return output_path
