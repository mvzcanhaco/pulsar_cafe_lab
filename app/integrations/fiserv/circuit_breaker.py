"""
Circuit Breaker para o cliente Fiserv/Sitef.

Estados:
  CLOSED   — operação normal, requisições passam.
  OPEN     — falhas acima do threshold; requisições bloqueadas até o timeout.
  HALF_OPEN — timeout expirou; uma requisição de teste é permitida.
             Se bem-sucedida → CLOSED. Se falhar → OPEN (reseta timer).
"""
import logging
import time
from enum import Enum
from threading import Lock

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """Lançado quando o circuit breaker está OPEN."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker ABERTO. Tente novamente em {retry_after:.1f}s."
        )


class CircuitBreaker:
    """
    Thread-safe circuit breaker.

    Args:
        failure_threshold: Número de falhas consecutivas para abrir o circuito.
        recovery_timeout:  Segundos no estado OPEN antes de tentar HALF_OPEN.
        half_open_successes: Sucessos consecutivos em HALF_OPEN para fechar o circuito.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_successes: int = 2,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_successes = half_open_successes

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at: float = 0.0
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        return self._state

    def allow_request(self) -> bool:
        """Retorna True se a requisição pode prosseguir."""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                elapsed = time.monotonic() - self._opened_at
                if elapsed >= self._recovery_timeout:
                    logger.info("Circuit breaker → HALF_OPEN (%.1fs decorridos)", elapsed)
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    return True
                return False

            # HALF_OPEN: permite apenas uma requisição de teste por vez
            return True

    def record_success(self) -> None:
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._half_open_successes:
                    logger.info("Circuit breaker → CLOSED após %d sucesso(s)", self._success_count)
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            if self._state == CircuitState.HALF_OPEN:
                logger.warning("Circuit breaker → OPEN (falha em HALF_OPEN)")
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()
            elif self._failure_count >= self._failure_threshold:
                logger.warning(
                    "Circuit breaker → OPEN após %d falha(s) consecutivas",
                    self._failure_count,
                )
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()

    def retry_after(self) -> float:
        """Segundos restantes até o próximo teste (apenas quando OPEN)."""
        elapsed = time.monotonic() - self._opened_at
        return max(0.0, self._recovery_timeout - elapsed)
