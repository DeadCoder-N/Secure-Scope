#!/bin/bash
# SecureScope — Stop All Services

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS_FILE="$ROOT/.pids"

echo ""
echo "Stopping SecureScope services..."

if [ -f "$PIDS_FILE" ]; then
  while IFS= read -r pid; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null
      echo "  ✓ Stopped PID $pid"
    fi
  done < "$PIDS_FILE"
  rm -f "$PIDS_FILE"
else
  # Fallback: kill by port
  for port in 3000 5001 5002 5003 8888; do
    pid=$(lsof -ti tcp:$port 2>/dev/null)
    if [ -n "$pid" ]; then
      kill "$pid" 2>/dev/null
      echo "  ✓ Stopped port $port (PID $pid)"
    fi
  done
fi

echo "All services stopped."
echo ""
