"""
Nexus Client Module
High-level HTTP client for the Nexus Agent Transaction Protocol (NATP).
Encapsulates envelope creation, signing, and transport.
"""

import requests
import logging
from typing import Dict, Any, Optional, List

from .crypto import IdentityManager
from .envelope import NexusEnvelope, SenderInfo, SettlementInfo

logger = logging.getLogger("nexus.client")


class NexusClient:
    """
    The main entry point for developers.
    Manages identity, discovery, and transactions.
    """

    def __init__(
            self,
            identity: IdentityManager,
            directory_url: str,
            orchestrator_url: str,
            agent_id: Optional[str] = None,
            api_key: Optional[str] = None
    ):
        self.identity = identity
        self.directory_url = directory_url.rstrip('/')
        self.orchestrator_url = orchestrator_url.rstrip('/')
        self.agent_id = agent_id
        self.api_key = api_key

        # Session for persistent connections
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-ATP-Key": self.api_key})

    def _create_envelope(self, payload: Dict[str, Any], priority: str = "normal") -> NexusEnvelope:
        """Helper to build and sign a standard envelope."""

        # 1. Build Sender Info
        sender = SenderInfo(
            public_key=self.identity.public_key_pem,
            agent_id=self.agent_id
        )

        # 2. Create Envelope
        # IMPORTANT: On injecte la priorité ici
        envelope = NexusEnvelope(
            priority=priority,
            sender=sender,
            payload=payload
            # settlement is default (0) for now
        )

        # 3. Sign Envelope
        envelope.sign(self.identity)

        return envelope

    def discover(self, service_type: str) -> List[Dict[str, Any]]:
        """
        P-7.1: Discover services from the Trust Directory.
        """
        url = f"{self.directory_url}/api/v1/services/search"
        try:
            resp = self.session.get(url, params={"service_type": service_type}, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return []

    def transact(self, service_contract: Dict[str, Any], payload: Dict[str, Any], priority: str = "normal") -> Optional[Dict[str, Any]]:
        """
        P-9.3: Execute a transaction via the Orchestrator.
        Wraps the payload in a signed NATP Envelope.

        Args:
            service_contract: The target service details.
            payload: The business data.
            priority: 'normal', 'high', or 'critical' (default: 'normal').
        """
        service_id = service_contract.get("service_id")
        if not service_id:
            logger.error("Invalid service contract: missing service_id")
            return None

        # Prepare the transaction payload
        transaction_payload = {
            "service_id": service_id,
            "consumer_agent_id": self.agent_id,
            "data": payload
        }

        # Create and Sign Envelope with Priority
        # IMPORTANT: On passe l'argument priority reçu
        envelope = self._create_envelope(transaction_payload, priority=priority)

        # Send to Orchestrator
        url = f"{self.orchestrator_url}/v1/a2a/transact"

        try:
            # Send the envelope as a dict (pydantic model_dump)
            resp = self.session.post(
                url,
                json=envelope.model_dump(mode='json'),
                timeout=30
            )

            if resp.status_code != 200:
                logger.error(f"Transaction Error {resp.status_code}: {resp.text}")

            resp.raise_for_status()

            return resp.json()

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return None