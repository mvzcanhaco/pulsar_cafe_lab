from app.data.repositories.sql_order_repository import _safe_order_state
from app.data.repositories.sql_payment_repository import _safe_card_type, _safe_result
from app.domain.models.order import OrderState
from app.domain.models.payment import CardType, PaymentResult


def test_safe_order_state_falls_back_to_open():
    assert _safe_order_state("OPEN") == OrderState.OPEN
    assert _safe_order_state("LEGACY") == OrderState.OPEN


def test_safe_payment_mappings_fallback():
    assert _safe_result("SUCCESS") == PaymentResult.SUCCESS
    assert _safe_result("LEGACY") == PaymentResult.FAIL
    assert _safe_card_type("CREDIT") == CardType.CREDIT
    assert _safe_card_type("LEGACY") == CardType.UNKNOWN
