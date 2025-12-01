"""
Amorce Client Module
High-level HTTP client for the Amorce Agent Transaction Protocol (AATP).
Encapsulates envelope creation, signing, and transport.
"""

import requests
import logging
from typing import Dict, Any, Optional, List

# Nouveaux imports pour la résilience
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .crypto import IdentityManager
from .envelope import AmorceEnvelope, SenderInfo, SettlementInfo, PriorityLevel
from .exceptions import AmorceConfigError, AmorceNetworkError, AmorceAPIError

logger = logging.getLogger("nexus.client")

# Production Mainnet Defaults (Zero-Config)
DEFAULT_DIRECTORY_URL = "https://directory.amorce.io"
DEFAULT_ORCHESTRATOR_URL = "https://orchestrator.amorce.io"


class AmorceClient:
    """
    The main entry point for developers.
    Manages identity, discovery, and transactions.
    """

    def __init__(
            self,
            identity: IdentityManager,
            directory_url: str = DEFAULT_DIRECTORY_URL,
            orchestrator_url: str = DEFAULT_ORCHESTRATOR_URL,
            agent_id: Optional[str] = None,
            api_key: Optional[str] = None
    ):
        """
        Initialize Amorce Client.
        
        Args:
            identity: IdentityManager instance for signing
            directory_url: Trust Directory URL (defaults to production mainnet)
            orchestrator_url: Orchestrator URL (defaults to production mainnet)
            agent_id: Optional override for agent ID
            api_key: Optional API key for L1 authentication
        
        Example:
            # Zero-config (uses production mainnet)
            client = AmorceClient(identity=identity)
            
            # Custom endpoints
            client = AmorceClient(
                identity=identity,
                directory_url="https://custom-dir.example.com",
                orchestrator_url="https://custom-orch.example.com"
            )
        """
        self.identity = identity
        
        if not directory_url.startswith(("http://", "https://")):
             raise AmorceConfigError(f"Invalid directory_url: {directory_url}")
        self.directory_url = directory_url.rstrip('/')

        if not orchestrator_url.startswith(("http://", "https://")):
             raise AmorceConfigError(f"Invalid orchestrator_url: {orchestrator_url}")
        self.orchestrator_url = orchestrator_url.rstrip('/')
        
        self.api_key = api_key

        # MCP 2.1: Read Agent ID directly from the identity derivation
        self.agent_id = agent_id if agent_id else identity.agent_id
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
            # FIX CRITIQUE L1: L'Orchestrateur attend X-API-Key, pas X-ATP-Key.
            self.session.headers.update({"X-API-Key": self.api_key})

    def _create_envelope(self, payload: Dict[str, Any], priority: str = PriorityLevel.NORMAL) -> AmorceEnvelope:
        """
        Legacy Helper: Maintained for internal consistency if needed,
        but transact() now uses flat payload construction.
        """
        # 1. Build Sender Info
        sender = SenderInfo(
            public_key=self.identity.public_key_pem,
            agent_id=self.agent_id
        )

        # 2. Create Envelope
        envelope = AmorceEnvelope(
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
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                 raise AmorceAPIError(f"Discovery API error: {e}", status_code=e.response.status_code, response_body=e.response.text)
            raise AmorceNetworkError(f"Discovery network error: {e}")
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            raise AmorceNetworkError(f"Discovery failed: {e}")

    def transact(self, service_contract: Dict[str, Any], payload: Dict[str, Any],
                 priority: str = PriorityLevel.NORMAL) -> Optional[Dict[str, Any]]:
        """
        P-9.3: Execute a transaction via the Orchestrator.
        FIX: Aligned with Orchestrator v1.4 protocol (Flat JSON + Header Signature).
        """
        service_id = service_contract.get("service_id")
        if not service_id:
            logger.error("Invalid service contract: missing service_id")
            return None

        # --- CORRECTION PROTOCOLE ---
        # 1. On construit le JSON "plat" attendu par le serveur
        request_body = {
            "service_id": service_id,
            "consumer_agent_id": self.agent_id,
            "payload": payload,
            "priority": priority
        }

        # 2. On signe ce JSON exact
        canonical_bytes = self.identity.get_canonical_json_bytes(request_body)
        signature = self.identity.sign_data(canonical_bytes)

        # 3. On met la signature DANS L'EN-TÊTE (Header)
        headers = {
            "X-Agent-Signature": signature,
            "Content-Type": "application/json"
        }

        # (La clé API L1 est déjà gérée par la session globale)

        url = f"{self.orchestrator_url}/v1/a2a/transact"

        try:
            # 4. On envoie : le JSON plat + les Headers avec la signature
            resp = self.session.post(
                url,
                json=request_body,
                headers=headers,
                timeout=30
            )

            if resp.status_code != 200:
                logger.error(f"Transaction Error {resp.status_code}: {resp.text}")
                raise AmorceAPIError(f"Transaction failed with status {resp.status_code}", status_code=resp.status_code, response_body=resp.text)

            return resp.json()

        except requests.exceptions.RequestException as e:
             raise AmorceNetworkError(f"Transaction network error: {e}")
        except AmorceAPIError:
             raise
        except Exception as e:
            logger.error(f"Transaction failed after retries: {e}")
            raise AmorceNetworkError(f"Transaction failed: {e}")