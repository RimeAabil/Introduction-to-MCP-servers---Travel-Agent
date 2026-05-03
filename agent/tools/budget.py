import re

import config
from agent.mcp_client import call_tool

SERVERS = config.SERVERS


def _extract_int(text: str) -> int | None:
    if not text:
        return None

    match = re.search(r"\b(\d+)\b", text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None

    try:
        return int(text)
    except ValueError:
        return None


def estimate_budget(query: str) -> str:
    """
    Estimate travel budget.
    Input format: 'destination, days, style'
    Example: 'Barcelona, 5, mid-range'
    """
    parts = [p.strip() for p in query.split(",")]
    destination = parts[0]
    days = _extract_int(parts[1]) if len(parts) > 1 else 5
    if days is None:
        return "Invalid days value. Please use a numeric days value, for example: 'Barcelona, 5, mid-range'."
    style = parts[2] if len(parts) > 2 else "mid-range"

    return call_tool(
        SERVERS["budget"],
        "BudgetEstimator",
        {"destination": destination, "days": days, "style": style},
    )
