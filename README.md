# Nexus Python SDK (NATP)

[![PyPI version](https://badge.fury.io/py/nexus-py-sdk.svg)](https://badge.fury.io/py/nexus-py-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Official Python SDK for the Nexus Agent Transaction Protocol (NATP).**

The Nexus SDK allows any Python application, API, or Agent to become a verified node in the **Agent Economy**. It provides the cryptographic primitives (Ed25519) and the transport layer required to transact securely with AI Agents (OpenAI, Google Gemini, Apple Intelligence).

---

## 🚀 Features

* **Zero-Trust Security**: Every request is cryptographically signed (Ed25519).
* **Agent Identity**: Manage your agent's identity and keys securely.
* **Priority Lane (v0.1.2)**: Mark critical messages to bypass network congestion.
* **Resilience (v0.1.2)**: Automatic retry logic with exponential backoff for unstable networks.
* **Type Safe**: Fully typed codebase (Pydantic models) for robust development.

---

## 📦 Installation

```bash
pip install nexus-py-sdk