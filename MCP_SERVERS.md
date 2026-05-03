# Introduction to MCP Servers — Travel Agent

## Overview

This repository is a hands-on course-style example of how to build a travel planning agent powered by Model Context Protocol (MCP) servers. It combines:

- a Streamlit front-end for interactive travel planning,
- a LangChain ReAct agent for reasoning and tool selection,
- multiple FastAPI-based MCP servers for deterministic tool execution,
- helper wrappers that let the agent call real services rather than rely solely on language-model predictions.

The goal is to demonstrate how to architect an agentic system where each piece is modular, testable, and explainable.

## What is an MCP Server?

An MCP server is a lightweight API service that exposes a well-defined capability over HTTP. In this project, each MCP server provides one focused function:

- budget estimation,
- weather lookup,
- currency conversion,
- destination search,
- arithmetic calculation.

The agent uses these servers as tools during planning. Instead of inventing numbers or recommendations from its own token distribution, the agent can make a tool call, receive a precise response, and continue reasoning based on that result.

## Why this architecture?

Using MCP servers brings several benefits:

- **Modularity:** Each capability lives in its own service.
- **Predictability:** Tool outputs are deterministic and auditable.
- **Transparency:** You can inspect individual tool APIs and their data.
- **Extendability:** New services can be added without changing the core agent.
- **Separation of concerns:** The agent reasons, servers execute.

## Repository Structure

- `app_streamlit.py` — Root compatibility wrapper for the Streamlit UI.
- `agents.py` — Root compatibility wrapper for the travel agent interface.
- `config.py` — Centralized MCP server URLs and shared runtime settings.
- `mcp_servers/` — FastAPI-based MCP server implementations.
- `agent/` — Travel agent package, including tool wrappers and prompts.
- `start_servers.sh` — Launch script for all MCP servers.
- `MCP_SERVERS.md` — Course-style documentation for the MCP server architecture.
- `README.md` — High-level project guidance and usage instructions.
- `requirements.txt` — Python dependencies.

## Core Components

### `mcp_servers/` folder

Each file in `mcp_servers/` is an independent FastAPI application exposing one tool:

- `budget_server.py`
- `weather_server.py`
- `currency_server.py`
- `destination_server.py`
- `calculator_server.py`

These services are intentionally simple, making them ideal for learning how tool-backed agents work.

### `agent/tools/`

Agent tools are thin wrappers around the MCP servers:

- `budget.py` calls the budget estimation server.
- `weather.py` calls the weather server.
- `currency.py` calls the currency conversion server.
- `destination.py` calls the destination search server.
- `calculator.py` calls the calculator server.

Each wrapper converts raw HTTP responses into a formatted string that the language model can understand.

### `agent/runner.py`

This file builds the travel agent using LangChain:

- `ChatOllama` is used as the LLM backend.
- `create_react_agent` creates a ReAct-style reasoning pipeline.
- `AgentExecutor` manages the thought/action/observation loop.

The agent receives tool definitions and the ReAct prompt from the `travel_agent` package.

### `app_streamlit.py`

A polished Streamlit interface that:

- checks MCP server health,
- renders example prompts,
- sends user input to `run_travel_agent()`,
- displays the resulting travel plan,
- offers a download button for the plan.

## Getting Started

### 1. Install dependencies

Create a virtual environment and install packages:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch MCP servers

Start all tool servers with:

```bash
./start_servers.sh
```

This will run each FastAPI server on a dedicated local port.

### 3. Start the Streamlit UI

Launch the front-end:

```bash
streamlit run app_streamlit.py
```

Open the displayed browser URL to interact with the travel planner.

### 4. Use the agent

Enter requests like:

- `Plan a 5-day mid-range trip to Barcelona in July. Show costs in EUR.`
- `I want a budget-friendly 3-day trip to Paris in December. Convert total to MAD.`
- `Plan a luxury 7-day trip to Tokyo in August. What's the weather like?`

The agent will call MCP tools automatically as needed.

## MCP Servers and Tool Flow

This project teaches the full flow from user intent to tool execution:

1. User enters a travel request.
2. The agent parses intent and decides which MCP tools to call.
3. It calls one or more server endpoints.
4. Each server returns structured JSON.
5. The agent observes the results and continues reasoning.
6. The final plan is returned to the user.

### Why this matters

In traditional LLM applications, models often hallucinate data or reasoning steps. MCP servers give the model access to real-service responses, making outputs more grounded and reliable.

## Running the Full System

Ports used by the project:

- `3001` — Budget Estimator
- `3002` — Weather Checker
- `3003` — Currency Converter
- `3004` — Destination Search
- `3005` — Calculator

The Streamlit app expects these services to be available locally.

## Extending the Project

To add a new MCP tool:

1. Add a new FastAPI server file under `mcp_servers/`.
2. Add a new endpoint with a clear request/response contract.
3. Add the service URL to `config.py`.
4. Create a wrapper in `agent/tools/`.
5. Add the tool to `agent/tools/__init__.py`.
6. Update the prompt or agent behavior if needed.

## Troubleshooting

- If the Streamlit UI reports a tool offline, verify `start_servers.sh` is running.
- If a server returns an error, inspect the service logs or access the endpoint directly.
- Ensure `venv/` is active and dependencies are installed.

## Course-style learning goals

This project is designed to teach:

- how to decompose agent capabilities into discrete services,
- how to use ReAct agents with tool invocation,
- why deterministic service outputs improve agent trust,
- how to wire tool wrappers to an LLM agent,
- how to build a local dev loop with Streamlit and FastAPI.

## License

Use this code for learning, experimentation, and MCP server exploration.
