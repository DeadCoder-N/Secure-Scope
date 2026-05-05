#!/bin/bash
# SecureScope — Start All Services
# Usage: ./start.sh

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS_FILE="$ROOT/.pids"
LOG_DIR="$ROOT/logs"

mkdir -p "$LOG_DIR"
> "$PIDS_FILE"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         SecureScope — Starting Up            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Kill anything already on our ports ──────────────────────────
echo "▶  Clearing ports 3000 5001 5002 5003 8888..."
for port in 3000 5001 5002 5003 8888; do
  pid=$(lsof -ti tcp:$port 2>/dev/null)
  if [ -n "$pid" ]; then
    kill $pid 2>/dev/null
    sleep 0.3
  fi
done
echo "   ✓ Ports cleared"
echo ""

# ── Start backend helper ─────────────────────────────────────────
start_backend() {
  local name="$1"
  local dir="$2"
  local port="$3"
  local script="$4"

  echo "▶  Starting $name on :$port..."

  if [ ! -d "$dir/venv" ]; then
    echo "   Installing Python deps for $name..."
    python3 -m venv "$dir/venv" > /dev/null 2>&1
    "$dir/venv/bin/pip" install -q -r "$dir/requirements.txt"
  fi

  "$dir/venv/bin/python" "$script" > "$LOG_DIR/${name}.log" 2>&1 &
  local pid=$!
  echo $pid >> "$PIDS_FILE"
  sleep 0.8

  # Verify it started
  if kill -0 $pid 2>/dev/null; then
    echo "   ✓ $name running (PID $pid)"
  else
    echo "   ✗ $name failed to start — check logs/$name.log"
  fi
}

# ── Start all backends ───────────────────────────────────────────
start_backend "tool1-vuln-scanner"  \
  "$ROOT/backends/tool1-vuln-scanner" 5001 \
  "$ROOT/backends/tool1-vuln-scanner/backend/app.py"

start_backend "tool2-sqli-tester"   \
  "$ROOT/backends/tool2-sqli-tester"  5002 \
  "$ROOT/backends/tool2-sqli-tester/backend/app.py"

start_backend "tool3-xss-scanner"   \
  "$ROOT/backends/tool3-xss-scanner"  5003 \
  "$ROOT/backends/tool3-xss-scanner/backend/app.py"

start_backend "vulnerable-target"   \
  "$ROOT/backends/vulnerable-target"  8888 \
  "$ROOT/backends/vulnerable-target/app.py"

# ── Start frontend ───────────────────────────────────────────────
echo ""
echo "▶  Starting frontend on :3000..."
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  echo "   Installing npm deps..."
  npm install --silent
fi
npm run dev -- --port 3000 > "$LOG_DIR/frontend.log" 2>&1 &
FE_PID=$!
echo $FE_PID >> "$PIDS_FILE"
cd "$ROOT"

# Wait for frontend to be ready
echo "   Waiting for frontend..."
for i in $(seq 1 15); do
  sleep 1
  if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✓ Frontend running (PID $FE_PID)"
    break
  fi
done

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           All Services Running               ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  SecureScope:       http://localhost:3000    ║"
echo "║  Vuln Scanner API:  http://localhost:5001    ║"
echo "║  SQLi Tester API:   http://localhost:5002    ║"
echo "║  XSS Scanner API:   http://localhost:5003    ║"
echo "║  VulnShop (demo):   http://localhost:8888    ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Logs: ./logs/                               ║"
echo "║  Stop: ./stop.sh                             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Open browser ─────────────────────────────────────────────────
echo "▶  Opening browser..."
sleep 1

# Detect OS and open browser
if command -v xdg-open > /dev/null 2>&1; then
  # Linux
  xdg-open http://localhost:3000 > /dev/null 2>&1 &
  sleep 0.5
  xdg-open http://localhost:8888 > /dev/null 2>&1 &
elif command -v open > /dev/null 2>&1; then
  # macOS
  open http://localhost:3000
  sleep 0.5
  open http://localhost:8888
fi

echo "   ✓ Browser opened"
echo ""
echo "   SecureScope → http://localhost:3000"
echo "   VulnShop    → http://localhost:8888"
echo ""
