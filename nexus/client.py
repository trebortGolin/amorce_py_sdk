"""
Nexus Client Module
High-level HTTP client for the Nexus Agent Transaction Protocol (NATP).
Encapsulates envelope creation, signing, and transport.
"""

import requests
import logging
from typing import Dict, Any, Optional, List

# Nouveaux imports pour la résilience
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .crypto import IdentityManager
from .envelope import NexusEnvelope, SenderInfo, SettlementInfo, PriorityLevel

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
            # MCP 2.0: Removed redundant agent_id argument
            api_key: Optional[str] = None
    ):
        self.identity = identity
        self.directory_url = directory_url.rstrip('/')
        self.orchestrator_url = orchestrator_url.rstrip('/')
        self.api_key = api_key

        # MCP 2.1: Read Agent ID directly from the identity derivation
        self.agent_id = identity.agent_id

        # Session for persistent connections
        self.session = requests.Session()

        # --- Configuration de la Résilience ---
        retry_strategy = Retry(
            total=3,  # Nombre total de tentatives après le premier échec
            backoff_factor=1,  # Attente: 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504],  # Codes à réessayer
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        # On monte l'adaptateur sur les deux protocoles
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        # -----------------------------------------------------

        if self.api_key:
            self.session.headers.update({"X-ATP-Key": self.api_key})

    def _create_envelope(self, payload: Dict[str, Any], priority: str = PriorityLevel.NORMAL) -> NexusEnvelope:
        """Helper to build and sign a standard envelope."""

        # 1. Build Sender Info
        sender = SenderInfo(
            public_key=self.identity.public_key_pem,
            agent_id=self.agent_id
        )

        # 2. Create Envelope
        envelope = NexusEnvelope(
            priority=priority,
            sender=sender,
            payload=payload
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
            # Le timeout est crucial ici pour ne pas bloquer indéfiniment
            resp = self.session.get(url, params={"service_type": service_type}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return []

    def transact(self, service_contract: Dict[str, Any], payload: Dict[str, Any], priority: str = PriorityLevel.NORMAL) -> Optional[Dict[str, Any]]:
        """
        P-9.3: Execute a transaction via the Orchestrator.
        Wraps the payload in a signed NATP Envelope.
        """
        service_id = service_contract.get("service_id")
        if not service_id:
            logger.error("Invalid service contract: missing service_id")
            return None

        transaction_payload = {
            "service_id": service_id,
            "consumer_agent_id": self.agent_id,
            "data": payload
        }

        envelope = self._create_envelope(transaction_payload, priority=priority)
        url = f"{self.orchestrator_url}/v1/a2a/transact"

        try:
            # L'appel réseau est maintenant protégé par le Retry automatique
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
            # Si on arrive ici, c'est que même les retries ont échoué
            logger.error(f"Transaction failed after retries: {e}")
            return None