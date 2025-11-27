# Nexus Python SDK (NATP)

**Official Python SDK for the Nexus Agent Transaction Protocol (NATP).**

The Nexus SDK allows any Python application, API, or Agent to become a verified node in the **Agent Economy**. It provides the cryptographic primitives (Ed25519) and the transport layer required to transact securely with AI Agents (OpenAI, Google Gemini, Apple Intelligence).

## 🚀 Features

-   **Zero-Trust Security**: Every request is cryptographically signed (Ed25519) locally.
    
-   **Agent Identity**: Manage your agent's identity and keys securely without complexity.
    
-   **Priority Lane**: Mark critical messages (`high`, `critical`) to bypass network congestion.
    
-   **Resilience**: Automatic retry logic with exponential backoff for unstable networks (handles 503, 429).
    
-   **Developer Experience (v0.1.6)**: Simplified `IdentityManager` with auto-derived Agent IDs.
    

## 📦 Installation

### Prerequisites

-   **Python 3.10+**
    
-   **OS**: Linux, macOS, or Windows.
    
    -   _Linux users:_ Ensure you have `build-essential` and `libssl-dev` installed for the cryptography dependency.
        

### Install via PyPI

```
pip install nexus-py-sdk

```

## ⚡ Quick Start

### 1. Identity Setup

An Agent is defined by its **Private Key**. Never share this key.

#### Option A: Quick Start (Ephemeral / Testing)

Generate a new identity in memory instantly. Perfect for QA scripts or temporary bots.

```
from nexus import IdentityManager

# Generates a fresh Ed25519 keypair in memory (Ephemeral)
identity = IdentityManager.generate_ephemeral()

# The Agent ID is automatically derived from the Public Key (SHA-256)
print(f"Agent ID: {identity.agent_id}")
print(f"Public Key: {identity.public_key_pem}")

```

#### Option B: Production (Secure Storage)

Load your identity from a secure source or environment variable.

```
import os
from nexus import IdentityManager, LocalFileProvider

# Load from a local PEM file
identity = IdentityManager(LocalFileProvider("agent_key.pem"))

# OR (Recommended) Load private key content from Environment Variable
# identity = IdentityManager.from_env("NEXUS_PRIVATE_KEY")

```

### 2. Sending a Transaction (Full Example)

Use the `NexusClient` to discover services and execute transactions.

```
import os
from nexus import NexusClient, PriorityLevel

# Configuration (Use Env Vars in Prod!)
DIRECTORY_URL = os.getenv("NEXUS_DIRECTORY_URL", "[https://directory.amorce.io](https://directory.amorce.io)")
ORCHESTRATOR_URL = os.getenv("NEXUS_ORCHESTRATOR_URL", "[https://api.amorce.io](https://api.amorce.io)")

# 1. Initialize the client
# Note: 'agent_id' is automatically derived from the identity object.
client = NexusClient(
    identity=identity,
    directory_url=DIRECTORY_URL,
    orchestrator_url=ORCHESTRATOR_URL
)

# 2. Define the payload (The "Letter" inside the Envelope)
payload = {
    "intent": "book_reservation",
    "params": {"date": "2025-10-12", "guests": 2}
}

# 3. Execute with PRIORITY
# Options: PriorityLevel.NORMAL, .HIGH, .CRITICAL
print(f"Sending transaction from {identity.agent_id}...")

try:
    response = client.transact(
        service_contract={"service_id": "srv_restaurant_01"},
        payload=payload,
        priority=PriorityLevel.HIGH 
    )
    
    if response.get("status") == "success":
        print(f"✅ Success! Tx ID: {response.get('transaction_id')}")
        print(f"Data: {response.get('data')}")
    else:
        print(f"⚠️ Server Error: {response}")

except Exception as e:
    print(f"❌ Network or Protocol Error: {str(e)}")

```

## 🛡️ Architecture & Security

The SDK implements the **NATP v0.1** standard strictly.

1.  **Envelope**: Data is wrapped in a `NexusEnvelope`.
    
2.  **Canonicalization**: JSON payloads are serialized canonically (RFC 8785) to ensure signature consistency.
    
3.  **Signing**: The envelope is signed locally using Ed25519.
    
4.  **Transport**: The envelope is sent via HTTP/2 to the Orchestrator.
    
5.  **Verification**: The receiver verifies the signature against the Trust Directory before processing.
    

## 🔧 Troubleshooting & FAQ

**Q: I get a `401 Unauthorized` when registering.** A: Ensure your signature logic is correct. If you use `IdentityManager`, the signature is handled automatically. If you are manually constructing payloads, verify you are signing the **canonical** JSON string encoded in UTF-8.

**Q: I get `SSL: CERTIFICATE_VERIFY_FAILED`.** A: This happens if you use a placeholder URL or a self-signed cert in dev. Ensure `ORCHESTRATOR_URL` points to a valid HTTPS endpoint with a trusted certificate.

**Q: How do I get my Agent ID?** A: Do not hardcode it. Access it via `identity.agent_id`. It is the SHA-256 hash of your public key.

## 🛠️ Development

To contribute to the SDK:

```
# Clone and install in editable mode
git clone [https://github.com/trebortGolin/nexus_py_sdk.git](https://github.com/trebortGolin/nexus_py_sdk.git)
cd nexus_py_sdk
pip install -e .

# Run Unit Tests
python3 -m unittest discover tests

```

## 📄 License

This project is licensed under the MIT License.