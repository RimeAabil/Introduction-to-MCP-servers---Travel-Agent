from mcp.server.fastmcp import FastMCP

RATES = {
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.5,
    "MAD": 10.1,
    "CAD": 1.36,
    "AUD": 1.52,
    "CHF": 0.90,
    "CNY": 7.24,
}


def convert_currency(amount_usd: float, target_currency: str) -> dict[str, object]:
    currency = target_currency.upper()
    if currency not in RATES:
        return {"error": f"Currency {currency} not supported. Supported: {list(RATES.keys())}"}

    rate = RATES[currency]
    return {
        "amount_usd": amount_usd,
        "target_currency": currency,
        "converted_amount": round(amount_usd * rate, 2),
        "exchange_rate": rate,
    }

from starlette.responses import PlainTextResponse

server = FastMCP(
    name="Currency Converter MCP Server",
    instructions="Convert USD amounts into supported foreign currencies.",
)
server.add_tool(
    convert_currency,
    name="CurrencyConverter",
    description="Convert a USD amount into another currency using fixed exchange rates.",
)
app = server.streamable_http_app()

def health(request):
    return PlainTextResponse("OK")

app.add_route("/health", health, methods=["GET"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3003)
