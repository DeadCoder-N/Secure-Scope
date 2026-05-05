@echo off
echo.
echo ╔══════════════════════════════════════════════╗
echo ║         SecureScope — Starting Up            ║
echo ╚══════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: ── Tool 1 — Vuln Scanner (5001) ─────────────────────────────
echo [1/5] Starting Vuln Scanner on :5001...
if not exist "backends\tool1-vuln-scanner\venv" (
    python -m venv backends\tool1-vuln-scanner\venv
    backends\tool1-vuln-scanner\venv\Scripts\pip install -q -r backends\tool1-vuln-scanner\requirements.txt
)
start "Tool1-VulnScanner" /min cmd /c "backends\tool1-vuln-scanner\venv\Scripts\python backends\tool1-vuln-scanner\backend\app.py"

:: ── Tool 2 — SQLi Tester (5002) ──────────────────────────────
echo [2/5] Starting SQLi Tester on :5002...
if not exist "backends\tool2-sqli-tester\venv" (
    python -m venv backends\tool2-sqli-tester\venv
    backends\tool2-sqli-tester\venv\Scripts\pip install -q -r backends\tool2-sqli-tester\requirements.txt
)
start "Tool2-SQLiTester" /min cmd /c "backends\tool2-sqli-tester\venv\Scripts\python backends\tool2-sqli-tester\backend\app.py"

:: ── Tool 3 — XSS Scanner (5003) ──────────────────────────────
echo [3/5] Starting XSS Scanner on :5003...
if not exist "backends\tool3-xss-scanner\venv" (
    python -m venv backends\tool3-xss-scanner\venv
    backends\tool3-xss-scanner\venv\Scripts\pip install -q -r backends\tool3-xss-scanner\requirements.txt
)
start "Tool3-XSSScanner" /min cmd /c "backends\tool3-xss-scanner\venv\Scripts\python backends\tool3-xss-scanner\backend\app.py"

:: ── Vulnerable Target — VulnShop (8888) ──────────────────────
echo [4/5] Starting VulnShop on :8888...
if not exist "backends\vulnerable-target\venv" (
    python -m venv backends\vulnerable-target\venv
    backends\vulnerable-target\venv\Scripts\pip install -q -r backends\vulnerable-target\requirements.txt
)
start "VulnShop" /min cmd /c "backends\vulnerable-target\venv\Scripts\python backends\vulnerable-target\app.py"

:: ── Frontend — React/Vite (3000) ─────────────────────────────
echo [5/5] Starting Frontend on :3000...
cd frontend
if not exist "node_modules" (
    echo     Installing npm deps...
    npm install --silent
)
start "Frontend" /min cmd /c "npm run dev"
cd ..

:: ── Wait and open browser ─────────────────────────────────────
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul
start http://localhost:3000
start http://localhost:8888

echo.
echo ╔══════════════════════════════════════════════╗
echo ║           All Services Running               ║
echo ╠══════════════════════════════════════════════╣
echo ║  SecureScope:       http://localhost:3000    ║
echo ║  Vuln Scanner API:  http://localhost:5001    ║
echo ║  SQLi Tester API:   http://localhost:5002    ║
echo ║  XSS Scanner API:   http://localhost:5003    ║
echo ║  VulnShop (demo):   http://localhost:8888    ║
echo ╠══════════════════════════════════════════════╣
echo ║  Close the minimized windows to stop.        ║
echo ╚══════════════════════════════════════════════╝
echo.
pause
