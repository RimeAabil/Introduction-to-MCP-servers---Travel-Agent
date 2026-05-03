"""
Travel agent — LangChain ReAct + Ollama (llama3:latest)
"""

from langchain_ollama import ChatOllama
from langchain_classic.agents import AgentExecutor, create_react_agent

try:
    from langchain_core.tools import Tool
except ImportError:
    try:
        from langchain.tools import Tool
    except ImportError:
        from langchain_classic.tools import Tool

from config import (
    OLLAMA_MODEL,
    TEMPERATURE,
    MAX_ITERATIONS,
    MAX_EXECUTION_TIME,
    EARLY_STOPPING_METHOD,
    VERBOSE,
)
from agent.prompts.react_prompt import get_react_prompt
from agent.tools.budget import estimate_budget
from agent.tools.calculator import calculate
from agent.tools.currency import convert_currency
from agent.tools.destination import search_destination
from agent.tools.weather import get_weather

# ── Helpers ────────────────────────────────────────────────────────────────────

_LIMIT_PHRASES = [
    "agent stopped due to iteration limit",
    "agent stopped due to time limit",
    "time limit",
    "iteration limit",
]

def _hit_limit(text: str) -> bool:
    return any(p in text.lower() for p in _LIMIT_PHRASES)

def _strip_quotes(s: str) -> str:
    return s.strip().strip("'\"")

# ── Cache dict shared across all tools in one agent run ───────────────────────
# Recreated fresh in TravelAgent.__init__ so each request starts clean.

def _make_tools(cache: dict) -> list:
    """
    Build Tool list where each function checks a shared cache first.
    If llama3 calls the same tool twice, it gets the cached result instantly
    instead of making another MCP call — no Pydantic subclassing needed.
    """

    def once(name: str, fn):
        def wrapper(q: str) -> str:
            if name in cache:
                return cache[name]   # silent cache hit, no extra text
            result = fn(_strip_quotes(q))
            cache[name] = result
            return result
        return wrapper

    return [
        Tool(
            name="WeatherChecker",
            func=once("WeatherChecker", get_weather),
            description=(
                "Get weather for a destination. "
                "Input: 'City' or 'City, month_number'. Example: Tokyo, 8"
            ),
        ),
        Tool(
            name="DestinationSearch",
            func=once("DestinationSearch", search_destination),
            description=(
                "Find attractions at a destination. "
                "Input: city name only. Example: Tokyo"
            ),
        ),
        Tool(
            name="BudgetEstimator",
            func=once("BudgetEstimator", estimate_budget),
            description=(
                "Estimate trip cost. "
                "Input: 'city, days, style'. Style: budget/mid-range/luxury. "
                "Example: Tokyo, 7, luxury"
            ),
        ),
        Tool(
            name="CurrencyConverter",
            func=once("CurrencyConverter", convert_currency),
            description=(
                "Convert USD to another currency. "
                "Input: 'amount, CODE'. Example: 1050, JPY"
            ),
        ),
        Tool(
            name="Calculator",
            func=once("Calculator", calculate),
            description=(
                "Do math. Input: expression. Example: 150 * 7"
            ),
        ),
    ]

# ── Prompt — ReAct instruction template ───────────────────────────────────────

REACT_PROMPT = get_react_prompt()

# ── Agent ──────────────────────────────────────────────────────────────────────

class TravelAgent:
    def __init__(self):
        self.llm = ChatOllama(model=OLLAMA_MODEL, temperature=TEMPERATURE)
        self._cache: dict = {}
        self.tools = _make_tools(self._cache)
        self.executor = self._create_executor()

    def _create_executor(self) -> AgentExecutor:
        react_agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=REACT_PROMPT,
        )
        return AgentExecutor(
            agent=react_agent,
            tools=self.tools,
            verbose=VERBOSE,
            max_iterations=MAX_ITERATIONS,
            max_execution_time=MAX_EXECUTION_TIME,
            early_stopping_method=EARLY_STOPPING_METHOD,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def process_request(self, user_request: str) -> str:
        try:
            response = self.executor.invoke({"input": user_request})
            output = response.get("output", "")

            if not output or _hit_limit(output):
                steps = response.get("intermediate_steps", [])
                if steps:
                    seen, lines = set(), []
                    for action, observation in steps:
                        if action.tool not in seen:
                            seen.add(action.tool)
                            lines.append(f"**{action.tool}** → {observation}")
                    if lines:
                        return (
                            "⚠️ Agent timed out — here's what it gathered:\n\n"
                            + "\n\n".join(lines)
                            + "\n\n*Tip: run `ollama pull mistral` for a much better experience.*"
                        )
                return "⚠️ Agent timed out. Check that your MCP servers are running."

            return output

        except Exception as e:
            return f"Error: {str(e)}"


def run_travel_agent(user_request: str) -> str:
    return TravelAgent().process_request(user_request)


if __name__ == "__main__":
    print(run_travel_agent("Plan a 7-day luxury trip to Tokyo in August."))