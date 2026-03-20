import pytest

from app.domain.models.payment import CardType, PaymentResult
from app.integrations.fiserv.sitef_result_parser import parse_sitef_response


def test_parse_success_response():
    raw = {
        "codigoResposta": "0",
        "nsu": "123456",
        "codigoAutorizacao": "AUTH001",
        "bandeira": "Visa",
        "ultimos4Digitos": "1234",
        "tipoCartao": "credito",
        "numeroParcelas": 1,
    }
    payment = parse_sitef_response(raw, order_id="order-1", amount_cents=1000)

    assert payment.result == PaymentResult.SUCCESS
    assert payment.nsu == "123456"
    assert payment.auth_code == "AUTH001"
    assert payment.card_brand == "Visa"
    assert payment.last4 == "1234"
    assert payment.card_type == CardType.CREDIT
    assert payment.error_message is None


def test_parse_cancel_response():
    raw = {"codigoResposta": "10"}
    payment = parse_sitef_response(raw, order_id="order-2", amount_cents=500)

    assert payment.result == PaymentResult.CANCEL
    assert payment.error_message == "Transação cancelada pelo usuário"


def test_parse_unknown_code_defaults_to_fail():
    raw = {"codigoResposta": "999"}
    payment = parse_sitef_response(raw, order_id="order-3", amount_cents=200)

    assert payment.result == PaymentResult.FAIL


def test_parse_pix_payment():
    raw = {
        "codigoResposta": "0",
        "tipoCartao": "pix",
        "nsu": "PIX001",
    }
    payment = parse_sitef_response(raw, order_id="order-4", amount_cents=300)

    assert payment.result == PaymentResult.SUCCESS
    assert payment.card_type == CardType.PIX


def test_parse_preserves_order_id_and_amount():
    raw = {"codigoResposta": "0"}
    payment = parse_sitef_response(raw, order_id="my-order", amount_cents=9999)

    assert payment.order_id == "my-order"
    assert payment.amount_cents == 9999
