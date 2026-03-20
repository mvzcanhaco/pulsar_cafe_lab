"""
Maps Sitef/Fiserv response codes to PaymentResult.
Mirrors SitefSaleResultParser.kt from the Android app (37 response codes).
"""
from app.domain.models.payment import CardType, Payment, PaymentResult

# Sitef response codes → PaymentResult
_RESPONSE_CODE_MAP: dict[str, PaymentResult] = {
    "0": PaymentResult.SUCCESS,
    "1": PaymentResult.AUTH,
    "2": PaymentResult.PARTIAL,
    "10": PaymentResult.CANCEL,
    "20": PaymentResult.FAIL,
    "21": PaymentResult.FAIL,
    "22": PaymentResult.FAIL,
    "23": PaymentResult.FAIL,
    "24": PaymentResult.FAIL,
    "25": PaymentResult.FAIL,
    "30": PaymentResult.FAIL,
    "40": PaymentResult.FAIL,
    "41": PaymentResult.FAIL,
    "42": PaymentResult.FAIL,
    "43": PaymentResult.FAIL,
    "44": PaymentResult.FAIL,
    "45": PaymentResult.FAIL,
    "50": PaymentResult.FAIL,
    "51": PaymentResult.FAIL,
    "52": PaymentResult.FAIL,
    "53": PaymentResult.FAIL,
    "54": PaymentResult.FAIL,
    "55": PaymentResult.FAIL,
    "56": PaymentResult.FAIL,
    "60": PaymentResult.FAIL,
    "70": PaymentResult.FAIL,
    "71": PaymentResult.FAIL,
    "72": PaymentResult.FAIL,
    "73": PaymentResult.FAIL,
    "74": PaymentResult.FAIL,
    "75": PaymentResult.FAIL,
    "80": PaymentResult.FAIL,
    "85": PaymentResult.FAIL,
    "90": PaymentResult.FAIL,
    "99": PaymentResult.FAIL,
}

_CARD_TYPE_MAP: dict[str, CardType] = {
    "credito": CardType.CREDIT,
    "debito": CardType.DEBIT,
    "voucher": CardType.VOUCHER,
    "pix": CardType.PIX,
}

_ERROR_MESSAGES: dict[str, str] = {
    "10": "Transação cancelada pelo usuário",
    "20": "Erro genérico",
    "21": "Timeout na comunicação com o Sitef",
    "22": "Erro de comunicação",
    "23": "Erro de configuração",
    "30": "Transação negada",
    "40": "Cartão inválido",
    "41": "Cartão expirado",
    "42": "Saldo insuficiente",
    "50": "Erro no PIN",
    "60": "Problema no terminal",
    "70": "Erro no servidor",
    "99": "Erro desconhecido",
}


def parse_sitef_response(raw: dict, order_id: str, amount_cents: int) -> Payment:
    """
    Converts a raw Sitef HTTP/socket response dict into a Payment domain object.
    """
    import uuid

    code = str(raw.get("codigoResposta", "99"))
    result = _RESPONSE_CODE_MAP.get(code, PaymentResult.FAIL)

    card_type_raw = str(raw.get("tipoCartao", "")).lower()
    card_type = _CARD_TYPE_MAP.get(card_type_raw, CardType.UNKNOWN)

    return Payment(
        id=str(uuid.uuid4()),
        order_id=order_id,
        amount_cents=amount_cents,
        result=result,
        card_type=card_type,
        nsu=str(raw.get("nsu", "")),
        auth_code=str(raw.get("codigoAutorizacao", "")),
        card_brand=str(raw.get("bandeira", "")),
        last4=str(raw.get("ultimos4Digitos", "")),
        installments=int(raw.get("numeroParcelas", 1)),
        merchant_receipt=str(raw.get("comprovanteEstabelecimento", "")),
        customer_receipt=str(raw.get("comprovantePortador", "")),
        error_message=_ERROR_MESSAGES.get(code) if result != PaymentResult.SUCCESS else None,
    )
