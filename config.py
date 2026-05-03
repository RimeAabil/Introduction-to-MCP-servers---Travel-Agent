# Configuration settings for the travel agent

# Ollama settings
# mistral:latest is significantly better than llama3 at following
# the strict ReAct format (Thought → Action → Action Input → Observation).
# Run: ollama pull mistral
OLLAMA_MODEL = "llama3:latest"
TEMPERATURE = 0.0

SERVERS = {
    "destination": "http://localhost:3004",
    "budget": "http://localhost:3001",
    "weather": "http://localhost:3002",
    "currency": "http://localhost:3003",
    "calculator": "http://localhost:3005",
}

MAX_ITERATIONS = 8           # llama3 loops — cut it off early
MAX_EXECUTION_TIME = 600.0
EARLY_STOPPING_METHOD = "force"
VERBOSE = True