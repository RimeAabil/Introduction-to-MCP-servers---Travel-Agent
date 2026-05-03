import re

import config
from agent.mcp_client import call_tool

SERVERS = config.SERVERS


def _clean_expression(expression: str) -> str:
    expression = expression.strip()
    if expression.startswith(("'", '"')) and expression.endswith(("'", '"')):
        expression = expression[1:-1].strip()

    # Remove words and units, keeping only valid math characters.
    expression = re.sub(r"[^0-9+\-*/()., ]+", " ", expression)
    expression = re.sub(r"\s+", " ", expression).strip()
    return expression


def calculate(expression: str) -> str:
    """
    Perform arithmetic calculations.
    Input: a math expression like '150 * 5 + 200'
    """
    cleaned = _clean_expression(expression)
    return call_tool(
        SERVERS["calculator"],
        "Calculator",
        {"expression": cleaned},
    )
