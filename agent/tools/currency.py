import re

import config
from agent.mcp_client import call_tool

SERVERS = config.SERVERS


def _extract_float(text: str) -> float | None:
    if not text:
        return None

    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", text)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None

    try:
        return float(text)
    except ValueError:
        return None


def convert_currency(query: str) -> str:
    """
    Convert USD to another currency.
    Input format: 'amount, CURRENCY_CODE'
    Example: '750, EUR'
    """
    parts = [p.strip() for p in query.split(",")]
    amount = _extract_float(parts[0])
    if amount is None:
        return "Invalid amount value. Please use a numeric amount, for example: '750, EUR'."

    currency = "EUR"
    if len(parts) > 1 and parts[1]:
        match = re.search(r"[A-Za-z]{3}", parts[1])
        if match:
            currency = match.group(0).upper()

    return call_tool(
        SERVERS["currency"],
        "CurrencyConverter",
        {"amount_usd": amount, "target_currency": currency},
    )
