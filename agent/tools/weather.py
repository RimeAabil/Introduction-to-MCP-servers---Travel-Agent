import re

import config
from agent.mcp_client import call_tool

SERVERS = config.SERVERS


def _extract_month(text: str) -> int | None:
    if not text:
        return None

    match = re.search(r"\b([1-9]|1[0-2])\b", text)
    if match:
        return int(match.group(1))

    try:
        return int(text)
    except ValueError:
        return None


def get_weather(query: str) -> str:
    """
    Get weather for a destination.
    Input format: 'destination' or 'destination, month_number'
    Example: 'Barcelona' or 'Barcelona, 7'
    """
    parts = [p.strip() for p in query.split(",")]
    destination = parts[0]
    arguments = {"destination": destination}

    if len(parts) > 1:
        month = _extract_month(parts[1])
        if month is None or not 1 <= month <= 12:
            return "Invalid month value. Please use a month number 1-12, for example: 'Barcelona, 7'."
        arguments["month"] = month

    return call_tool(
        SERVERS["weather"],
        "WeatherChecker",
        arguments,
    )
