"""
FiservSitefClient — HTTP client que envia requisições de venda ao servidor
Fiserv/Sitef (ClienteSitef) rodando local ou remotamente no POS.

Funcionalidades:
  - Retry com backoff exponencial via tenacity (falhas de rede/timeout)
  - Circuit breaker: protege o terminal de sobrecarga após falhas repetidas
  - Logging estruturado com order_id em cada evento

Reference: Fiserv CliSiTef documentation (CliSiTef 4.0+)
"""
import logging
import uuid

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryError,
)

from app.domain.models.payment import Payment, PaymentResult
from app.integrations.fiserv.circuit_breaker import CircuitBreaker, CircuitOpenError
from app.integrations.fiserv.sitef_result_parser import parse_sitef_response
from app.integrations.fiserv.sitef_sale_config import SitefSaleConfig
from app.integrations.fiserv.sitef_sale_request import SitefSaleRequest

logger = logging.getLogger(__name__)

# Circuit breaker compartilhado na instância (pode ser injetado para testes)
_DEFAULT_CIRCUIT_BREAKER = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
    half_open_successes=2,
)


class FiservSitefClient:
    """
    Async HTTP client para o servidor Fiserv Sitef CliSiTef.
    Inclui retry automático e circuit breaker.
    Todos os métodos são coroutines — use `await`.
    """

    def __init__(
        self,
        config: SitefSaleConfig,
        circuit_breaker: CircuitBreaker | None = None,
    ) -> None:
        self._config = config
        self._base_url = f"http://{config.sitef_ip}:{config.sitef_port}"
        self._cb = circuit_breaker or _DEFAULT_CIRCUIT_BREAKER

    async def process_sale(self, request: SitefSaleRequest) -> Payment:
        """
        Inicia uma transação de venda no terminal POS conectado.
        Retorna um objeto Payment com o resultado.

        Lança CircuitOpenError se o circuit breaker estiver aberto.
        """
        if not self._cb.allow_request():
            logger.warning(
                "Circuit breaker OPEN — bloqueando requisição order=%s", request.order_id
            )
            raise CircuitOpenError(self._cb.retry_after())

        try:
            payment = await self._send_with_retry(request)
            self._cb.record_success()
            return payment
        except (httpx.TimeoutException, httpx.ConnectError, RetryError) as exc:
            self._cb.record_failure()
            logger.error(
                "Sitef indisponível após retries para order=%s: %s",
                request.order_id,
                exc,
            )
            return self._timeout_payment(request)
        except httpx.HTTPStatusError as exc:
            self._cb.record_failure()
            logger.error(
                "Sitef HTTP error order=%s status=%s",
                request.order_id,
                exc.response.status_code,
            )
            return self._error_payment(request, str(exc))

    async def _send_with_retry(self, request: SitefSaleRequest) -> Payment:
        """Executa a chamada HTTP com backoff exponencial."""

        @retry(
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        async def _attempt() -> Payment:
            payload = {
                **request.to_api_dict(),
                "empresaSitef": self._config.company_id,
                "terminalSitef": self._config.terminal_id,
                "isvAppId": self._config.isv_app_id,
                "versaoApi": self._config.api_version,
            }

            logger.info(
                "Enviando venda ao Sitef: order=%s amount=%d (tentativa)",
                request.order_id,
                request.amount_cents,
            )

            async with httpx.AsyncClient(timeout=self._config.timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/Sale", json=payload)
                response.raise_for_status()
                raw = response.json()

            payment = parse_sitef_response(raw, request.order_id, request.amount_cents)
            logger.info(
                "Resposta Sitef: order=%s result=%s nsu=%s",
                request.order_id,
                payment.result,
                payment.nsu,
            )
            return payment

        return await _attempt()

    def _timeout_payment(self, request: SitefSaleRequest) -> Payment:
        return Payment(
            id=str(uuid.uuid4()),
            order_id=request.order_id,
            amount_cents=request.amount_cents,
            result=PaymentResult.FAIL,
            error_message="Timeout na comunicação com o Sitef após retries",
        )

    def _error_payment(self, request: SitefSaleRequest, message: str) -> Payment:
        return Payment(
            id=str(uuid.uuid4()),
            order_id=request.order_id,
            amount_cents=request.amount_cents,
            result=PaymentResult.FAIL,
            error_message=message,
        )
