"""
Amorce Python SDK - The Standard for Secure AI Agent Transactions
"""

__version__ = "0.2.2"

# Core clients
from .client import AmorceClient
from .core.async_client import AsyncAmorceClient

# Identity management
from .crypto import (
    IdentityManager,
    LocalFileProvider,
    EnvVarProvider,
    GoogleSecretManagerProvider,
)

# Request verification (for Builders)
from .verification import verify_request, VerifiedRequest

# Protocol primitives
from .envelope import (
    AmorceEnvelope,
    SenderInfo,
    SettlementInfo,
    PriorityLevel,
)

# Models
from .models import AmorceConfig, AmorceResponse, TransactionResult

# Exceptions
from .exceptions import (
    AmorceError,
    AmorceConfigError,
    AmorceNetworkError,
    AmorceAPIError,
    AmorceSecurityError,
    AmorceValidationError,
)

# MCP Integration
from .mcp_helpers import MCPToolClient

# A2A Well-Known Manifest (NEW)
from .well_known import (
    serve_well_known,
    serve_well_known_fastapi,
    serve_well_known_flask,
    fetch_manifest,
    fetch_manifest_sync,
    generate_manifest_file,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "AmorceClient",
    "AsyncAmorceClient",
    # Identity
    "IdentityManager",
    "LocalFileProvider",
    "EnvVarProvider",
    "GoogleSecretManagerProvider",
    # Verification (for Builders)
    "verify_request",
    "VerifiedRequest",
    # Protocol
    "AmorceEnvelope",
    "SenderInfo",
    "SettlementInfo",
    "PriorityLevel",
    # Models
    "AmorceConfig",
    "AmorceResponse",
    "TransactionResult",
    # Exceptions
    "AmorceError",
    "AmorceConfigError",
    "AmorceNetworkError",
    "AmorceAPIError",
    "AmorceSecurityError",
    "AmorceValidationError",
    # MCP Integration
    "MCPToolClient",
    # A2A Well-Known (NEW)
    "serve_well_known",
    "serve_well_known_fastapi",
    "serve_well_known_flask",
    "fetch_manifest",
    "fetch_manifest_sync",
    "generate_manifest_file",
]

print(f"Amorce SDK v{__version__} loaded.")