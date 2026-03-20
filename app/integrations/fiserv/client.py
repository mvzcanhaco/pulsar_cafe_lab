"""
FiservSitefClient — HTTP client that sends sale requests to the Fiserv/Sitef
server (ClienteSitef) running locally or remotely on the POS.

The Sitef ClienteSitef exposes a local HTTP API on port 4096 (default).
This client wraps that API and translates responses to domain Payment objects.

Reference: Fiserv CliSiTef documentation (CliSiTef 4.0+)
"""
import logging

import httpx

from app.domain.models.payment import Payment, PaymentResult
from app.integrations.fiserv.sitef_result_parser import parse_sitef_response
from app.integrations.fiserv.sitef_sale_config import SitefSaleConfig
from app.integrations.fiserv.sitef_sale_request import SitefSaleRequest

logger = logging.getLogger(__name__)


class FiservSitefClient:
    """
    Async HTTP client for the Fiserv Sitef CliSiTef local server.
    All methods are coroutines — call with `await`.
    """

    def __init__(self, config: SitefSaleConfig) -> None:
        self._config = config
        self._base_url = f"http://{config.sitef_ip}:{config.sitef_port}"

    async def process_sale(self, request: SitefSaleRequest) -> Payment:
        """
        Initiates a sale transaction on the connected POS terminal.
        Returns a Payment domain object with the result.
        """
        payload = {
            **request.to_api_dict(),
            "empresaSitef": self._config.company_id,
            "terminalSitef": self._config.terminal_id,
            "isvAppId": self._config.isv_app_id,
            "versaoApi": self._config.api_version,
        }

        logger.info("Sending sale request to Sitef: order=%s amount=%d", request.order_id, request.amount_cents)

        try:
            async with httpx.AsyncClient(timeout=self._config.timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/Sale", json=payload)
                response.raise_for_status()
                raw = response.json()
        except httpx.TimeoutException:
            logger.error("Sitef request timed out for order %s", request.order_id)
            return self._timeout_payment(request)
        except httpx.HTTPError as exc:
            logger.error("Sitef HTTP error for order %s: %s", request.order_id, exc)
            return self._error_payment(request, str(exc))

        payment = parse_sitef_response(raw, request.order_id, request.amount_cents)
        logger.info("Sitef response: order=%s result=%s nsu=%s", request.order_id, payment.result, payment.nsu)
        return payment

    def _timeout_payment(self, request: SitefSaleRequest) -> Payment:
        import uuid
        return Payment(
            id=str(uuid.uuid4()),
            order_id=request.order_id,
            amount_cents=request.amount_cents,
            result=PaymentResult.FAIL,
            error_message="Timeout na comunicação com o Sitef",
        )

    def _error_payment(self, request: SitefSaleRequest, message: str) -> Payment:
        import uuid
        return Payment(
            id=str(uuid.uuid4()),
            order_id=request.order_id,
            amount_cents=request.amount_cents,
            result=PaymentResult.FAIL,
            error_message=message,
        )
