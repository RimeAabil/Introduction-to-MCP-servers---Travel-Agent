# 🌍 Travel Agent — MCP Server Architecture

> A production-style travel planning assistant powered by a **LangChain ReAct agent**, **local LLMs via Ollama**, and **modular MCP tool servers** built with FastAPI.

---

## What This Project Does

You type a travel request like:

> *"Plan a 5-day mid-range trip to Barcelona in July. Show costs in EUR."*

The system:
1. Passes your request to a **reasoning agent** (powered by a local LLM)
2. The agent decides which tools it needs — weather, budget, currency, destinations
3. Each tool is a separate **MCP server** that returns precise, structured data
4. The agent assembles the results into a complete travel plan
5. The plan is displayed in a clean **Streamlit UI** with a download option

This architecture separates *reasoning* (the LLM) from *execution* (the MCP servers), making the system modular, testable, and reliable.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                        │
│              ui/streamlit_app.py · port 8501            │
└────────────────────────┬────────────────────────────────┘
                         │ user request
                         ▼
┌─────────────────────────────────────────────────────────┐
│              LangChain ReAct Agent                      │
│         agent/runner.py · ChatOllama (llama3)           │
│                                                         │
│  thinks → picks tool → calls MCP → observes → repeats  │
└──┬──────────┬──────────┬────────────┬──────────┬────────┘
   │          │          │            │          │
   ▼          ▼          ▼            ▼          ▼
Budget    Weather    Currency    Destination  Calculator
:3001      :3002      :3003        :3004       :3005
```

---

## Project Structure

```
travel-agent/
│
├── agent/                      # Agent logic
│   ├── runner.py               # Builds and runs the ReAct agent
│   ├── mcp_client.py           # HTTP client for calling MCP servers
│   ├── prompts/                # Agent prompt templates
│   └── tools/                  # Tool wrappers (one per MCP server)
│       ├── budget.py
│       ├── weather.py
│       ├── currency.py
│       ├── destination.py
│       └── calculator.py
│
├── mcp_servers/                # Independent FastAPI tool services
│   ├── budget_server.py        # Travel budget estimation
│   ├── weather_server.py       # Destination weather lookup
│   ├── currency_server.py      # USD currency conversion
│   ├── destination_server.py   # Attraction & food recommendations
│   └── calculator_server.py    # Safe arithmetic evaluation
│
├── ui/
│   └── streamlit_app.py        # Streamlit front-end
│
├── config.py                   # Centralized URLs and model settings
├── app_streamlit.py            # Root entrypoint for Streamlit
├── agents.py                   # Root compatibility wrapper
├── start_servers.sh            # Launches all MCP servers at once
├── requirements.txt            # All Python dependencies
├── README.md                   # This file
└── MCP_SERVERS.md              # Deep-dive into MCP server architecture
```

---

## Quick Start

### 1. Clone and set up the environment

```bash
cd /home/rime/projects/travel-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Ollama and pull the model

```bash
# In a separate terminal
ollama serve

# Pull the model (one-time)
ollama pull llama3
```

### 3. Launch all MCP servers

```bash
./start_servers.sh
```

This starts 5 FastAPI services on dedicated ports:

| Port | Service |
|------|---------|
| 3001 | Budget Estimator |
| 3002 | Weather Checker |
| 3003 | Currency Converter |
| 3004 | Destination Search |
| 3005 | Calculator |

### 4. Start the Streamlit UI

```bash
streamlit run app_streamlit.py
```

Open the URL shown in the terminal (typically **http://localhost:8501**).

---

## Example Requests

```
Plan a 5-day mid-range trip to Barcelona in July. Show costs in EUR.

I want a budget-friendly 3-day trip to Paris in December. Convert total to MAD.

Plan a luxury 7-day trip to Tokyo in August. What's the weather like?
```

---

## How the Agent Works

The agent uses the **ReAct** (Reasoning + Acting) pattern:

```
Thought:  I need to check the weather in Barcelona in July.
Action:   weather_tool
Input:    "Barcelona, July"
Observation: Avg temp 28°C, mostly sunny, low rainfall.

Thought:  Now I need to estimate the budget for 5 days mid-range.
Action:   budget_tool
Input:    "Barcelona, 5 days, mid-range"
Observation: ~$1,200 USD total.

Thought:  Convert to EUR.
Action:   currency_tool
Input:    "1200 USD to EUR"
Observation: ~€1,104

...Final Answer: [complete travel plan]
```

Each tool call hits a real MCP server — no hallucinated numbers.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tool shows "offline" in UI | Run `./start_servers.sh` |
| Agent gives no answer | Check Ollama is running: `ollama serve` |
| Port already in use | Kill the process: `lsof -ti:3001 \| xargs kill` |
| Model not found | Run `ollama pull llama3` |
| Dependency error | Activate venv: `source venv/bin/activate` |

---

## Extending the Project

To add a new MCP tool:

1. Create `mcp_servers/my_tool_server.py` — a FastAPI app with one endpoint
2. Add its URL to `config.py`
3. Create `agent/tools/my_tool.py` — a wrapper that calls the server
4. Register it in `agent/tools/__init__.py`
5. Add it to the tool list in `agent/runner.py`
6. Update the agent prompt if needed

See `MCP_SERVERS.md` for a full technical walkthrough.

---

## License

For learning, experimentation, and MCP server exploration.
