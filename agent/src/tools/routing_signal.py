"""Emissor de sinal de handover para o Gateway Go."""

import httpx

from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)


class HandoverSignal:
    """Emissor de eventos de handover."""

    def __init__(self, gateway_url: str = "http://backend:8080"):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=5.0)

    async def emit(
        self,
        session_id: str,
        reason: str,
        target_level: int,
        risk_score: float,
    ) -> bool:
        """Emite sinal de handover para o Gateway."""
        payload = {
            "type": "handover_request",
            "session_id": session_id,
            "reason": reason,
            "target_level": target_level,
            "risk_score": risk_score,
        }

        try:
            logger.info(
                "Emitindo sinal de handover",
                session_id=session_id,
                target_level=target_level,
            )

            response = await self.client.post(
                f"{self.gateway_url}/internal/handover",
                json=payload,
            )

            if response.status_code == 200:
                logger.info("Handover aceito pelo Gateway", session_id=session_id)
                return True
            else:
                logger.warning(
                    "Handover rejeitado",
                    session_id=session_id,
                    status_code=response.status_code,
                )
                return False

        except Exception as e:
            logger.error(
                "Erro ao emitir handover",
                session_id=session_id,
                error=str(type(e).__name__),
            )
            return False

    async def close(self) -> None:
        """Fecha cliente HTTP."""
        await self.client.aclose()


# Singleton
handover_signal = HandoverSignal()
