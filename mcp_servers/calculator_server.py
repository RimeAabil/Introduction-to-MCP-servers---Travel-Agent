import re
from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse


def _normalize_expression(expression: str) -> str:
    expression = expression.strip()
    if expression.startswith(("'", '"')) and expression.endswith(("'", '"')):
        expression = expression[1:-1].strip()
    expression = re.sub(r"[^0-9+\-*/()., ]+", " ", expression)
    expression = re.sub(r"\s+", " ", expression).strip()
    return expression


def calculate(expression: str) -> dict[str, object]:
    expression = _normalize_expression(expression)
    if not expression:
        return {"error": "Invalid or empty expression"}

    allowed = set("0123456789+-*/()., ")
    if not all(c in allowed for c in expression):
        return {"error": "Invalid characters in expression"}

    try:
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as exc:
        return {"error": str(exc)}

server = FastMCP(
    name="Calculator MCP Server",
    instructions="Evaluate simple arithmetic expressions for the travel assistant.",
)
server.add_tool(
    calculate,
    name="Calculator",
    description="Evaluate arithmetic expressions and return the numeric result.",
)
app = server.streamable_http_app()


def health(request):
    return PlainTextResponse("OK")

app.add_route("/health", health, methods=["GET"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3005)
