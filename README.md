
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

## 🛠️ Development & Verification

To contribute to the SDK or verify a deployment, follow these steps.

### 1. Environment Setup

It is strictly recommended to use a Virtual Environment to avoid conflicts.

Bash

```
# Clone the repository
git clone [https://github.com/trebortGolin/nexus_py_sdk.git](https://github.com/trebortGolin/nexus_py_sdk.git)
cd nexus_py_sdk

# Create and activate Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

```

### 2. Running the QA Suite (Smoke Test)

We provide a specialized QA script to validate core v0.1.6 features (Identity Derivation, Client API, and Envelope Aliases).

**Command:**

Bash

```
python3 tests/test_smoke.py

```

**Expected Output:** The script checks 3 critical components. You should see:

-   ✅ `[PASS] Agent ID is mathematically correct (SHA-256).`
    
-   ✅ `[PASS] NexusClient retrieved Agent ID from identity.`
    
-   ✅ `[PASS] Envelope created with alias 'Envelope' and priority 'critical'.`
    

### 3. Running Integration Tests

To test resilience and network retry logic (requires a local mock server):

Bash

```
python3 tests/test_resilience_real.py

```

----------

## 📄 License

This project is licensed under the MIT License.