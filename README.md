# Introduction to MCP Servers — Travel Agent

## What this project is

This repository is a full example of a tool-backed travel planning application built with Model Context Protocol (MCP) servers. It demonstrates how to combine:

- a user-facing interface powered by Streamlit,
- a ReAct-style language agent powered by LangChain and Ollama,
- multiple independent MCP tool servers implemented with FastAPI,
- a clean package layout so each part of the system is easy to understand.

The main idea is to keep reasoning and tool execution separate. The agent decides what to do, and the MCP servers execute deterministic operations with clear inputs and outputs.

## Professional project structure

- `agent/` — travel agent package
  - `mcp_client.py` — MCP tool client implementation
  - `prompts/` — agent prompt templates
  - `tools/` — wrappers that convert agent tool requests into MCP calls
  - `runner.py` — agent construction and execution logic
- `mcp_servers/` — FastAPI tool server implementations
- `ui/` — Streamlit front-end source
- `config.py` — centralized configuration for server URLs and model settings
- `start_servers.sh` — convenient startup script for all MCP services
- `MCP_SERVERS.md` — detailed course-style MCP server documentation
- `requirements.txt` — Python dependencies for the full system

## How the system works

### 1. User interface

The user interacts with the system through a Streamlit app. The Streamlit UI is implemented in `ui/streamlit_app.py` and provides:

- sample travel prompts,
- a text input for custom requests,
- tool health checks for each MCP service,
- rendered travel plan output,
- a download button to save the plan.

### 2. Agent reasoning

The travel agent is defined in `agent/runner.py`. It uses:

- `ChatOllama` for local model inference,
- LangChain ReAct for the thought/action/observation loop,
- a set of named tools to call external MCP services.

The agent is configured to follow a structured prompt template with clear tool usage instructions.

### 3. MCP servers

The real tool work happens in `mcp_servers/`. Each server provides one capability:

- `budget_server.py` — travel budget estimation,
- `weather_server.py` — destination weather lookup,
- `currency_server.py` — USD currency conversion,
- `destination_server.py` — attraction and food recommendations,
- `calculator_server.py` — safe arithmetic evaluation.

These servers are intentionally small and designed to be easy to read and extend.

### 4. Tool wrappers

The agent uses wrapper functions in `agent/tools/` to translate the model's tool input into MCP calls. Each wrapper:

- parses a flexible string input,
- validates or extracts the relevant values,
- calls the appropriate MCP service via `agent.mcp_client.call_tool`,
- returns a plain text result for the agent to consume.

## Setup and run

### Requirements

This project requires Python and the packages listed in `requirements.txt`.

### Install dependencies

```bash
cd /home/rime/projects/travel-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start the MCP servers

```bash
./start_servers.sh
```

The script starts each server on a dedicated local port:

- `3001` — Budget Estimator
- `3002` — Weather Checker
- `3003` — Currency Converter
- `3004` — Destination Search
- `3005` — Calculator

### Run the Streamlit app

```bash
streamlit run app_streamlit.py
```

Then open the browser address that Streamlit prints.

## Example prompts

- `Plan a 5-day mid-range trip to Barcelona in July. Show costs in EUR.`
- `I want a budget-friendly 3-day trip to Paris in December. Convert total to MAD.`
- `Plan a luxury 7-day trip to Tokyo in August. What's the weather like?`

## Extending the project

To add a new MCP tool:

1. Add a new FastAPI service under `mcp_servers/`.
2. Add the service URL to `config.py`.
3. Add a wrapper under `agent/tools/`.
4. Add the new tool to `agent/runner.py`.
5. Update the prompt or agent logic if needed.

## Notes on the new structure

This repo is now organized into clear, descriptive folders that reflect each responsibility:

- `agent/` for agent logic and tool integration,
- `mcp_servers/` for independent HTTP tool services,
- `ui/` for the frontend experience.

That makes the code easier to navigate, maintain, and present as a professional demo.

## License

Use this repository for learning and exploration.
