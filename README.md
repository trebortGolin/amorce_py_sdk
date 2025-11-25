```
```
# Nexus Python SDK (NATP)

[![PyPI version](https://badge.fury.io/py/nexus-py-sdk.svg)](https://badge.fury.io/py/nexus-py-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Official Python SDK for the Nexus Agent Transaction Protocol (NATP).**

The Nexus SDK allows any Python application, API, or Agent to become a verified node in the **Agent Economy**. It provides the cryptographic primitives (Ed25519) and the transport layer required to transact securely with AI Agents.

---

## 🚀 Features

* **Zero-Trust Security**: Every request is cryptographically signed (Ed25519).
* **Agent Identity**: Manage your agent's identity and keys securely.
* **Priority Lane**: Mark critical messages (`high`, `critical`) to bypass network congestion.
* **Resilience**: Automatic retry logic with exponential backoff for unstable networks.
* **Developer Experience (v0.1.6)**: Simplified identity management and Agent ID auto-derivation.

---

## 📦 Installation

```bash
pip install nexus-py-sdk

```

----------

## ⚡ Quick Start

### 1. Identity Setup

An Agent is defined by its Private Key. **Never share this key.**

#### Option A: Quick Start (Ephemeral / Testing)

Generate a new identity in memory instantly. No files required.

Python

```
from nexus import IdentityManager

# Generates a fresh Ed25519 keypair in memory (Ephemeral)
identity = IdentityManager.generate_ephemeral()

print(f"Agent Public Key: {identity.public_key_pem}")
print(f"Agent ID (Derived): {identity.agent_id}")

```

#### Option B: Production (Secure Storage)

Load your identity from a secure source.

Python

```
from nexus import IdentityManager, LocalFileProvider

# Load from a local PEM file
identity = IdentityManager(LocalFileProvider("agent_key.pem"))

```

### 2. Sending a Transaction

Use the `NexusClient` to discover services and execute transactions.

Python

```
from nexus import NexusClient, PriorityLevel

# Initialize the client
# Note: 'agent_id' is now automatically derived from the identity (v0.1.6)
client = NexusClient(
    identity=identity,
    directory_url="[https://directory.amorce.io](https://directory.amorce.io)",
    orchestrator_url="[https://api.amorce.io](https://api.amorce.io)"
)

# Define the payload
payload = {
    "intent": "book_reservation",
    "params": {"date": "2025-10-12", "guests": 2}
}

# Execute with PRIORITY
# Options: PriorityLevel.NORMAL, .HIGH, .CRITICAL
response = client.transact(
    service_contract={"service_id": "srv_restaurant_01"},
    payload=payload,
    priority=PriorityLevel.HIGH 
)

print(response)

```

----------

## 🛡️ Architecture

The SDK implements the **NATP v0.1** standard.

1.  **Envelope**: Data is wrapped in a `NexusEnvelope`, serialized canonically, and signed.
    
2.  **Transport**: The envelope is sent via HTTP/2 to the Orchestrator with automatic retries.
    
3.  **Verification**: The receiver verifies the signature against the Trust Directory before processing.
    

----------

## 🛠️ Development

### Running Tests

To ensure the SDK works in your environment:

Bash

```
# Install test dependencies
pip install -r requirements.txt

# Run the integration test
python3 tests/test_resilience_real.py

```

----------

## 📄 License

This project is licensed under the MIT License.