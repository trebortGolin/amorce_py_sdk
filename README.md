# Nexus Python SDK (NATP)

**Official Python SDK for the Nexus Agent Transaction Protocol (NATP).**

The Nexus SDK allows any Python application, API, or Agent to become a verified node in the Agent Economy. It provides the cryptographic primitives (Ed25519) and the transport layer required to transact securely with AI Agents (OpenAI, Google Gemini, Apple Intelligence).

## 🚀 Features

* **Zero-Trust Security:** Every request is cryptographically signed (Ed25519).
* **Agent Identity:** Manage your agent's identity and keys securely.
* **Priority Lane (v0.1.2):** Mark critical messages (`high`, `critical`) to bypass network congestion.
* **Resilience (v0.1.2):** Automatic retry logic with exponential backoff for unstable networks (handles 503, 429, etc.).
* **Type Safe:** Fully typed codebase (Pydantic models) for robust development.

## 📦 Installation

Install via pip:

```bash
pip install nexus-py-sdk
For development from source:

Bash

git clone [https://github.com/trebortGolin/nexus_py_sdk.git](https://github.com/trebortGolin/nexus_py_sdk.git)
cd nexus_py_sdk
pip install .
⚡ Quick Start
1. Identity Setup
An Agent is defined by its Private Key. Never share this key.

Python

from nexus.crypto import IdentityManager, LocalFileProvider

# Load your identity from a local PEM file
# (In production, use EnvVarProvider or GoogleSecretManagerProvider)
identity = IdentityManager(LocalFileProvider("agent_key.pem"))

print(f"Agent Public Key: {identity.public_key_pem}")
2. Sending a Transaction
Use the NexusClient to discover services and execute transactions.

Python

from nexus.client import NexusClient

# Initialize the client
client = NexusClient(
    identity=identity,
    directory_url="[https://directory.amorce.io](https://directory.amorce.io)",
    orchestrator_url="[https://api.amorce.io](https://api.amorce.io)",
    agent_id="your-agent-uuid"
)

# Define the payload
payload = {
    "intent": "book_reservation",
    "params": {"date": "2025-10-12", "guests": 2}
}

# Execute with PRIORITY (v0.1.2 feature)
# Options: 'normal', 'high', 'critical'
# The client will automatically retry if the network is unstable.
response = client.transact(
    service_contract={"service_id": "srv_restaurant_01"},
    payload=payload,
    priority="high" 
)

print(response)
🛡️ Architecture
The SDK implements the NATP v0.1 standard.

Envelope: Data is wrapped in a NexusEnvelope, serialized canonically, and signed.

New in v0.1.2: Includes a priority field validated strictly by regex.

Transport: The envelope is sent via HTTP/2 to the Orchestrator.

New in v0.1.2: Implements exponential backoff (Retry-After) for reliability.

Verification: The receiver verifies the signature against the Trust Directory before processing.

🛠️ Development
Running Tests
To ensure the SDK works in your environment (especially the new Resilience logic):

Bash

# Install test dependencies
pip install -r requirements.txt

# Run the real-world integration test (spawns a local server)
python3 tests/test_resilience_real.py
📄 License
This project is licensed under the MIT License.