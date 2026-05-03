# MCP Servers — Technical Deep Dive

> A complete guide to understanding, building, and extending the MCP (Model Context Protocol) servers in this project.

---

## Table of Contents

1. [What is an MCP Server?](#1-what-is-an-mcp-server)
2. [Why MCP Instead of Plain LLM?](#2-why-mcp-instead-of-plain-llm)
3. [How MCP Servers Fit Into the Agent Loop](#3-how-mcp-servers-fit-into-the-agent-loop)
4. [MCP Server Anatomy](#4-mcp-server-anatomy)
5. [The Five MCP Servers in This Project](#5-the-five-mcp-servers-in-this-project)
6. [The MCP Client](#6-the-mcp-client)
7. [Tool Wrappers — Bridging Agent and Server](#7-tool-wrappers--bridging-agent-and-server)
8. [Data Flow — End to End](#8-data-flow--end-to-end)
9. [Running and Testing MCP Servers](#9-running-and-testing-mcp-servers)
10. [Adding a New MCP Server](#10-adding-a-new-mcp-server)
11. [Design Principles](#11-design-principles)

---

## 1. What is an MCP Server?

An **MCP server** (Model Context Protocol server) is a lightweight, self-contained HTTP API service that exposes exactly one capability to an AI agent.

Think of it as a **tool the agent can pick up and use**. Instead of the language model guessing or inventing an answer, it asks the MCP server — which returns a precise, deterministic result.

In this project, each MCP server is a small **FastAPI application** running on its own local port. The agent calls these servers the same way a web browser calls a website: it sends an HTTP request, and gets a JSON response back.

### A simple analogy

Imagine a travel agency where:
- The **agent** is the senior consultant who thinks and plans
- Each **MCP server** is a specialist department (weather desk, finance desk, destination desk)
- The consultant asks each department for specific facts, then assembles the final plan

The consultant doesn't invent the exchange rate — they call the finance desk. That's exactly what MCP servers enable.

---

## 2. Why MCP Instead of Plain LLM?

Language models are excellent at reasoning, summarizing, and writing — but they have real weaknesses for factual, numerical data:

| Problem | Example | MCP Solution |
|---------|---------|--------------|
| Hallucinated numbers | LLM invents a $900 hotel budget | Budget server returns a calculated estimate |
| Stale knowledge | LLM doesn't know today's exchange rate | Currency server fetches or computes it |
| Unreliable recommendations | LLM recommends a restaurant that closed | Destination server queries real data |
| Math errors | LLM miscalculates totals | Calculator server evaluates arithmetic exactly |

By routing specific tasks to MCP servers, you get:

- **Accuracy** — tool outputs are deterministic and verifiable
- **Auditability** — you can inspect what each server returned
- **Modularity** — each capability is isolated and independently testable
- **Trust** — the agent can't "make up" a weather report if it must call the weather server

---

## 3. How MCP Servers Fit Into the Agent Loop

This project uses the **ReAct** (Reasoning + Acting) pattern. The agent alternates between thinking and acting until it has a complete answer.

```
┌─────────────────────────────────────────────────────────┐
│                      ReAct Loop                         │
│                                                         │
│  1. THOUGHT   "I need to check the weather in Tokyo"    │
│                          │                              │
│  2. ACTION    Calls weather_tool("Tokyo, August")       │
│                          │                              │
│  3. MCP CALL  HTTP POST → weather_server:3002           │
│                          │                              │
│  4. RESPONSE  { "temp": "31°C", "condition": "sunny" }  │
│                          │                              │
│  5. OBSERVE   Agent reads and understands the result    │
│                          │                              │
│  6. THOUGHT   "Now I need the budget for 7 days luxury" │
│                          │                              │
│       [ Loop continues until final answer ]             │
└─────────────────────────────────────────────────────────┘
```

The agent never sees the HTTP calls — it just sees the text result returned by each tool wrapper. The MCP architecture is invisible to the model; it only knows it has tools with names and descriptions.

---

## 4. MCP Server Anatomy

Every MCP server in this project follows the same structure:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My Tool Server")

# 1. Define the input model
class MyRequest(BaseModel):
    param_one: str
    param_two: int

# 2. Define the output model
class MyResponse(BaseModel):
    result: str
    detail: dict

# 3. Expose one focused endpoint
@app.post("/tool-name", response_model=MyResponse)
def my_tool(req: MyRequest):
    # deterministic logic here
    return MyResponse(result="...", detail={})

# 4. Health check (used by the UI to show server status)
@app.get("/health")
def health():
    return {"status": "ok"}
```

### Key design rules

- **One endpoint per server** — each server does one thing
- **Typed inputs and outputs** — Pydantic models validate everything
- **No randomness** — given the same input, always return the same output
- **Always include `/health`** — the Streamlit UI polls this to show live status
- **Fail clearly** — return meaningful errors, not silent failures

---

## 5. The Five MCP Servers in This Project

### 5.1 Budget Estimator — port 3001

**File:** `mcp_servers/budget_server.py`

Estimates total travel cost based on destination, duration, and travel style.

**Endpoint:** `POST /estimate-budget`

```json
Request:
{
  "destination": "Barcelona",
  "days": 5,
  "style": "mid-range"
}

Response:
{
  "total_usd": 1200,
  "daily_usd": 240,
  "breakdown": {
    "accommodation": 600,
    "food": 300,
    "transport": 200,
    "activities": 100
  }
}
```

**Why this matters:** Without this server, the agent would invent budget figures. With it, estimates are consistent and explainable.

---

### 5.2 Weather Checker — port 3002

**File:** `mcp_servers/weather_server.py`

Returns typical weather conditions for a destination and travel month.

**Endpoint:** `POST /get-weather`

```json
Request:
{
  "destination": "Tokyo",
  "month": "August"
}

Response:
{
  "avg_temp_c": 31,
  "condition": "Hot and humid",
  "rainfall_mm": 150,
  "advice": "Pack light clothing and stay hydrated."
}
```

**Why this matters:** Weather is critical for packing advice and activity planning. This server gives consistent seasonal data.

---

### 5.3 Currency Converter — port 3003

**File:** `mcp_servers/currency_server.py`

Converts a USD amount into a target currency.

**Endpoint:** `POST /convert`

```json
Request:
{
  "amount_usd": 1200,
  "target_currency": "EUR"
}

Response:
{
  "converted_amount": 1104,
  "currency": "EUR",
  "rate": 0.92
}
```

**Why this matters:** Users often want costs shown in their local currency (MAD, EUR, GBP). The agent can't reliably compute this itself.

---

### 5.4 Destination Search — port 3004

**File:** `mcp_servers/destination_server.py`

Returns top attractions and food recommendations for a destination.

**Endpoint:** `POST /search`

```json
Request:
{
  "destination": "Paris",
  "category": "attractions"
}

Response:
{
  "destination": "Paris",
  "attractions": ["Eiffel Tower", "Louvre Museum", "Montmartre"],
  "restaurants": ["Le Comptoir du Relais", "Septime"],
  "tips": "Book Louvre tickets online to skip the queue."
}
```

**Why this matters:** Recommendations need to be grounded in real places. This server provides a curated, reliable list.

---

### 5.5 Calculator — port 3005

**File:** `mcp_servers/calculator_server.py`

Safely evaluates arithmetic expressions.

**Endpoint:** `POST /calculate`

```json
Request:
{
  "expression": "1200 * 0.92 + 50"
}

Response:
{
  "result": 1154.0,
  "expression": "1200 * 0.92 + 50"
}
```

**Why this matters:** LLMs frequently make arithmetic errors, especially with multi-step calculations. The calculator server eliminates this entirely.

---

## 6. The MCP Client

**File:** `agent/mcp_client.py`

The MCP client is the agent's HTTP interface to all the servers. It handles:

- sending requests to the correct server URL
- serializing inputs to JSON
- deserializing JSON responses
- handling connection errors gracefully

```python
def call_tool(server_url: str, endpoint: str, payload: dict) -> dict:
    """
    Send a POST request to an MCP server and return the JSON response.
    """
    url = f"{server_url}/{endpoint}"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
```

All tool wrappers go through this single function, which means:
- error handling is centralized
- timeouts are consistent
- you can add logging or retries in one place

---

## 7. Tool Wrappers — Bridging Agent and Server

**Folder:** `agent/tools/`

Each tool wrapper is a Python function that:

1. Receives a **raw string** from the LLM (e.g. `"Barcelona, 5 days, mid-range"`)
2. Parses and validates that string into structured parameters
3. Calls `mcp_client.call_tool()` with the right server URL and payload
4. Formats the JSON response into a **plain text string** the LLM can read

```python
# agent/tools/budget.py

from agent.mcp_client import call_tool
from config import BUDGET_SERVER_URL

def budget_tool(input_str: str) -> str:
    """
    Input: "Barcelona, 5 days, mid-range"
    Output: A plain-text budget summary for the agent to read.
    """
    parts = [p.strip() for p in input_str.split(",")]
    destination = parts[0]
    days = int(parts[1].split()[0])
    style = parts[2] if len(parts) > 2 else "mid-range"

    result = call_tool(BUDGET_SERVER_URL, "estimate-budget", {
        "destination": destination,
        "days": days,
        "style": style,
    })

    return (
        f"Estimated budget for {days} days in {destination} ({style}): "
        f"${result['total_usd']} USD (${result['daily_usd']}/day). "
        f"Breakdown: Accommodation ${result['breakdown']['accommodation']}, "
        f"Food ${result['breakdown']['food']}, "
        f"Transport ${result['breakdown']['transport']}, "
        f"Activities ${result['breakdown']['activities']}."
    )
```

### Why plain text output?

The agent (the LLM) reads tool outputs as part of its context window. JSON is not ideal — plain natural language is easier for the model to reason about and integrate into its final response.

---

## 8. Data Flow — End to End

Here is the complete journey of a single user request:

```
User: "Plan a 5-day mid-range trip to Barcelona in July. Show costs in EUR."
         │
         ▼
Streamlit UI (ui/streamlit_app.py)
  → calls run_travel_agent(user_input)
         │
         ▼
Agent Runner (agent/runner.py)
  → constructs AgentExecutor with tools + ReAct prompt
  → invokes agent with user input
         │
         ▼
ReAct Loop (LangChain + ChatOllama)
  → Thought: "Check weather for Barcelona in July"
  → Action: weather_tool("Barcelona, July")
         │
         ▼
Tool Wrapper (agent/tools/weather.py)
  → parses "Barcelona, July"
  → calls mcp_client.call_tool(WEATHER_SERVER_URL, "get-weather", {...})
         │
         ▼
MCP Server (mcp_servers/weather_server.py · port 3002)
  → receives POST /get-weather
  → returns { "avg_temp_c": 28, "condition": "Warm and sunny", ... }
         │
         ▼
Tool Wrapper (returns formatted text to agent)
  "Barcelona in July: avg 28°C, warm and sunny, low rainfall. Great for outdoor sightseeing."
         │
         ▼
Agent continues loop → calls budget_tool → calls currency_tool → ...
         │
         ▼
Final Answer: Complete 5-day travel plan with weather, budget in EUR, and top recommendations
         │
         ▼
Streamlit UI displays the plan with a download button
```

---

## 9. Running and Testing MCP Servers

### Start all servers

```bash
./start_servers.sh
```

### Test a server directly (no agent needed)

```bash
# Test the weather server
curl -X POST http://localhost:3002/get-weather \
  -H "Content-Type: application/json" \
  -d '{"destination": "Tokyo", "month": "August"}'

# Test the budget server
curl -X POST http://localhost:3001/estimate-budget \
  -H "Content-Type: application/json" \
  -d '{"destination": "Barcelona", "days": 5, "style": "mid-range"}'

# Test the calculator
curl -X POST http://localhost:3005/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "1200 * 0.92"}'
```

### Check server health

```bash
curl http://localhost:3001/health   # Budget
curl http://localhost:3002/health   # Weather
curl http://localhost:3003/health   # Currency
curl http://localhost:3004/health   # Destination
curl http://localhost:3005/health   # Calculator
```

Each should return `{"status": "ok"}`.

### View auto-generated API docs

FastAPI automatically generates interactive docs for every server:

```
http://localhost:3001/docs   # Budget Estimator
http://localhost:3002/docs   # Weather Checker
http://localhost:3003/docs   # Currency Converter
http://localhost:3004/docs   # Destination Search
http://localhost:3005/docs   # Calculator
```

Open any of these in a browser to explore and test the API interactively.

---

## 10. Adding a New MCP Server

Follow these 5 steps to add a new capability (e.g. a flight search tool):

### Step 1 — Create the server

```python
# mcp_servers/flights_server.py

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Flight Search Server")

class FlightRequest(BaseModel):
    origin: str
    destination: str
    month: str

class FlightResponse(BaseModel):
    avg_price_usd: int
    airline: str
    duration_hours: float

@app.post("/search-flights", response_model=FlightResponse)
def search_flights(req: FlightRequest):
    # your logic here
    return FlightResponse(avg_price_usd=450, airline="Example Air", duration_hours=2.5)

@app.get("/health")
def health():
    return {"status": "ok"}
```

### Step 2 — Add the URL to config

```python
# config.py
FLIGHTS_SERVER_URL = "http://localhost:3006"
```

### Step 3 — Add it to start_servers.sh

```bash
uvicorn mcp_servers.flights_server:app --port 3006 &
```

### Step 4 — Create the tool wrapper

```python
# agent/tools/flights.py

from agent.mcp_client import call_tool
from config import FLIGHTS_SERVER_URL

def flights_tool(input_str: str) -> str:
    parts = [p.strip() for p in input_str.split(",")]
    result = call_tool(FLIGHTS_SERVER_URL, "search-flights", {
        "origin": parts[0],
        "destination": parts[1],
        "month": parts[2],
    })
    return f"Avg flight from {parts[0]} to {parts[1]}: ${result['avg_price_usd']} USD on {result['airline']} ({result['duration_hours']}h)."
```

### Step 5 — Register the tool in the agent

```python
# agent/runner.py

from agent.tools.flights import flights_tool
from langchain.tools import Tool

tools = [
    # ... existing tools ...
    Tool(
        name="flights_tool",
        func=flights_tool,
        description="Search for flight prices. Input: 'origin, destination, month'"
    ),
]
```

That's all. The agent will now use the new tool automatically when it determines flight data is needed.

---

## 11. Design Principles

This project is built around a set of deliberate architectural choices:

### Separation of concerns

The agent reasons. The servers execute. These responsibilities are never mixed. The LLM never performs arithmetic — it calls the calculator. It never estimates prices — it calls the budget server.

### One server, one job

Each MCP server has exactly one endpoint that does one thing. This makes servers easy to understand, test, debug, and replace independently.

### Determinism over prediction

Tool outputs are deterministic. Given the same input, a server always returns the same output. This is fundamentally different from asking an LLM to "guess" the same information — and far more reliable.

### Plain text at the agent boundary

JSON is great for machines; natural language is great for language models. Tool wrappers always convert structured JSON into clear, readable text before returning it to the agent.

### Fail loudly

Servers raise proper HTTP errors when input is invalid or a service is unavailable. Silent failures make debugging impossible. The Streamlit UI surfaces server health in real time so you always know what's working.

### Easy to extend

The architecture is intentionally open-ended. Adding a new capability never requires modifying existing servers or the agent core — just add a new server, a new wrapper, and register the tool. Each piece is independently testable.

---

*For setup instructions and example prompts, see [README.md](./README.md).*
