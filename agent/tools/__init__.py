# Tool registry and factory
from typing import List, Dict, Any
from langchain_classic.tools import Tool
from .destination import search_destination
from .budget import estimate_budget
from .weather import get_weather
from .currency import convert_currency
from .calculator import calculate

# Tool definitions with their metadata
TOOL_DEFINITIONS = [
    {
        "name": "DestinationSearch",
        "func": search_destination,
        "description": (
            "Use this to find tourist attractions, landmarks, activities, and food "
            "recommendations for a travel destination. Input: city name only. "
            "Example: 'Barcelona'"
        )
    },
    {
        "name": "BudgetEstimator",
        "func": estimate_budget,
        "description": (
            "Use this to estimate total travel costs in USD. "
            "Input format: 'destination, number_of_days, style' "
            "where style is budget, mid-range, or luxury. "
            "Example: 'Barcelona, 5, mid-range'"
        )
    },
    {
        "name": "WeatherChecker",
        "func": get_weather,
        "description": (
            "Use this to get weather conditions for a destination. "
            "Input format: 'destination' or 'destination, month_number (1-12)'. "
            "Example: 'Barcelona, 7' for July weather."
        )
    },
    {
        "name": "CurrencyConverter",
        "func": convert_currency,
        "description": (
            "Use this to convert USD amounts to another currency. "
            "Input format: 'amount_in_usd, CURRENCY_CODE'. "
            "Supported codes: EUR, GBP, JPY, MAD, CAD, AUD, CHF, CNY. "
            "Example: '750, EUR'"
        )
    },
    {
        "name": "Calculator",
        "func": calculate,
        "description": (
            "Use this for arithmetic calculations during reasoning. "
            "Input: a math expression as a string. "
            "Example: '150 * 5 + 200'"
        )
    },
]

def get_all_tools() -> List[Tool]:
    """Create and return all LangChain Tool objects."""
    return [
        Tool(
            name=tool_def["name"],
            func=tool_def["func"],
            description=tool_def["description"]
        )
        for tool_def in TOOL_DEFINITIONS
    ]

def get_tool_names() -> List[str]:
    """Return list of all tool names."""
    return [tool_def["name"] for tool_def in TOOL_DEFINITIONS]