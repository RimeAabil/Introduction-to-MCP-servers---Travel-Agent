from mcp.server.fastmcp import FastMCP

BASE_COSTS = {
    "budget": 50,
    "mid-range": 150,
    "luxury": 300,
}

EXPENSIVE_CITIES = {"paris", "tokyo", "new york", "zurich", "london"}


def estimate_budget(destination: str, days: int = 5, style: str = "mid-range") -> dict[str, object]:
    """Estimate travel budget in USD."""
    daily_rate = BASE_COSTS.get(style, 150)
    if destination.lower() in EXPENSIVE_CITIES:
        daily_rate *= 1.5

    total_cost = daily_rate * days
    return {
        "destination": destination,
        "days": days,
        "style": style,
        "daily_rate_usd": round(daily_rate, 2),
        "total_usd": round(total_cost, 2),
    }

from starlette.responses import PlainTextResponse

server = FastMCP(
    name="Budget Estimator MCP Server",
    instructions="Estimate travel budget using destination, days, and travel style.",
)
server.add_tool(
    estimate_budget,
    name="BudgetEstimator",
    description="Estimate a travel budget in USD based on destination, days, and travel style.",
)
app = server.streamable_http_app()

def health(request):
    return PlainTextResponse("OK")

app.add_route("/health", health, methods=["GET"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3001)
