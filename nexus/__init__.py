# Nexus SDK Core
# Version 0.1.6

__version__ = "0.1.6"

# Task 1: Crypto & Identity
from .crypto import IdentityManager, LocalFileProvider, EnvVarProvider, GoogleSecretManagerProvider

# Task 2: Protocol Envelope
# DX FIX: Aliasing NexusEnvelope to Envelope for simpler imports
from .envelope import NexusEnvelope, NexusEnvelope as Envelope, PriorityLevel

# Task 3: Client
from .client import NexusClient

# Flattening exports as requested by QA Ticket
__all__ = [
    "NexusClient",
    "NexusEnvelope",
    "Envelope",
    "PriorityLevel",
    "IdentityManager",
    "LocalFileProvider",
    "EnvVarProvider",
    "GoogleSecretManagerProvider"
]