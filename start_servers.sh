#!/bin/bash
# Starts all 5 MCP tool servers in the background

echo "Starting MCP Tool Servers..."

uvicorn mcp_servers.budget_server:app --port 3001 &
echo "[+] Budget Calculator running on port 3001"

uvicorn mcp_servers.weather_server:app --port 3002 &
echo "[+] Weather Tool running on port 3002"

uvicorn mcp_servers.currency_server:app --port 3003 &
echo "[+] Currency Converter running on port 3003"

uvicorn mcp_servers.destination_server:app --port 3004 &
echo "[+] Destination Search running on port 3004"

uvicorn mcp_servers.calculator_server:app --port 3005 &
echo "[+] Calculator running on port 3005"

echo ""
echo "All servers running. Press Ctrl+C to stop all."
wait