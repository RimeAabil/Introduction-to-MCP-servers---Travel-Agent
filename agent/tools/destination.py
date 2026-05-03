import config
from agent.mcp_client import call_tool

SERVERS = config.SERVERS


def search_destination(destination: str) -> str:
    """Search for attractions and activities at a destination."""
    return call_tool(
        SERVERS["destination"],
        "DestinationSearch",
        {"destination": destination},
    )
