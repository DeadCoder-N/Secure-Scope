# SecureScope — Engineering Final Year Project Plan (v2)

**Project:** SecureScope — Web Application Security Testing Platform  
**Stack:** React + Vite + TypeScript + Tailwind CSS | Python + Flask  
**Tools:** 3 production-grade security tools  
**Status:** Phase 1 In Progress

---

## Vision

Two completely separate experiences in one project:

### Mode 1 — SecureScope Platform
Unified dashboard. All 3 tools in one place. Shared navbar, shared design system.
Professional security platform feel.

### Mode 2 — Individual Tools
Each tool is a fully self-contained mini-app. Own layout, own header, own dashboard,
own report generation. If you extract just one tool page it feels like a complete product.

---

## Route Structure

```
/                        → Landing page (selector between Platform and Individual Tools)
/dashboard               → Platform home (3 tool cards)
/dashboard/vuln-scanner  → Vuln scanner in platform context
/dashboard/sql-injection → SQLi tester in platform context
/dashboard/xss-scanner   → XSS scanner in platform context

/tools                   → Individual tools listing page
/tools/vuln-scanner      → Standalone vuln scanner (own layout, own header)
/tools/sql-injection     → Standalone SQLi tester (own layout, own header)
/tools/xss-scanner       → Standalone XSS scanner (own layout, own header)
```

---

## Design System — Dark Arrogant Minimalist

### Colors
```
Background:    #0a0a0f   (near black, slight blue tint)
Surface:       #111118   (cards, panels)
Surface-2:     #1a1a24   (elevated elements, inputs)
Border:        rgba(255,255,255,0.07)
Border-hover:  rgba(255,255,255,0.12)
Accent:        #06b6d4   (cyan — used sparingly)
Accent-glow:   rgba(6,182,212,0.15)
Accent-dim:    rgba(6,182,212,0.08)
Text-primary:  #f1f5f9
Text-secondary:#94a3b8
Text-muted:    #475569
Critical:      #ef4444
High:          #f97316
Medium:        #eab308
Low:           #22c55e
Info:          #06b6d4
```

### Typography
- Font: Inter (weights 400, 500, 600, 700)
- Mono: JetBrains Mono (scan logs, code, payloads)
- Large headings: tight letter-spacing (-0.02em), heavy weight
- No decorative fonts

### Key Design Rules
- Near-black background, NOT pure black
- Cards have 1px border, NO box shadows
- Accent cyan used ONLY on: active states, key numbers, CTAs, scan results
- Subtle radial glow on landing page (faint cyan, top center)
- Hover states: border brightens, no color floods
- Buttons: filled for primary action, ghost for secondary
- NO glassmorphism, NO gradient rainbows, NO floating blobs

---

## Real-time Scan Log

Full-width terminal block during scanning. Collapses when results appear.

### During scan:
```
┌─────────────────────────────────────────────────────┐
│ ● SCANNING  localhost:8888/user?id=1                │
│─────────────────────────────────────────────────────│
│ [14:23:01] Initializing scanner...                  │
│ [14:23:02] Target: http://localhost:8888/user?id=1  │
│ [14:23:02] Parameters found: id                     │
│ [14:23:03] Testing param 'id' — error-based...      │
│ [14:23:04] → Payload #3: SQL error detected ⚠       │
│ [14:23:04] → Running control verification...        │
│ [14:23:05] ✓ CONFIRMED: Error-Based SQLi [CRITICAL] │
│                                                     │
│ ████████████████████░░░░  82%                       │
└─────────────────────────────────────────────────────┘
```

### After scan:
- Terminal collapses
- Results appear
- Small "▸ View scan log" toggle at top of results to re-expand

---

## Project Structure (Final)

```
SecureScope/
├── PLAN.md
├── start.sh
├── stop.sh
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Landing.tsx              ← NEW: selector page
│       │   ├── platform/
│       │   │   ├── PlatformHome.tsx     ← dashboard with 3 cards
│       │   │   ├── VulnScannerPage.tsx
│       │   │   ├── SQLInjectionPage.tsx
│       │   │   └── XSSScannerPage.tsx
│       │   └── tools/
│       │       ├── ToolsHome.tsx        ← NEW: individual tools listing
│       │       ├── StandaloneVuln.tsx   ← NEW: self-contained vuln tool
│       │       ├── StandaloneSQLi.tsx   ← NEW: self-contained sqli tool
│       │       └── StandaloneXSS.tsx    ← NEW: self-contained xss tool
│       ├── components/
│       │   ├── layout/
│       │   │   ├── PlatformNav.tsx      ← platform navbar
│       │   │   └── ToolNav.tsx          ← NEW: standalone tool header
│       │   └── shared/
│       │       ├── ScanTerminal.tsx     ← NEW: real-time log terminal
│       │       ├── ScanProgress.tsx
│       │       ├── SeverityBadge.tsx
│       │       ├── DownloadButtons.tsx
│       │       └── VulnCard.tsx
│       ├── index.css                    ← complete dark theme
│       └── App.tsx                      ← updated routes
│
└── backends/
    ├── tool1-vuln-scanner/
    ├── tool2-sqli-tester/              ← upgraded payloads (60-90)
    ├── tool3-xss-scanner/              ← upgraded payloads (40-60)
    └── vulnerable-target/
```

---

## Ports

| Service              | Port |
|----------------------|------|
| Frontend (Vite)      | 3000 |
| Tool 1 — Vuln Scanner| 5001 |
| Tool 2 — SQLi Tester | 5002 |
| Tool 3 — XSS Scanner | 5003 |
| Vulnerable Target    | 8080 |

---

## Tool 1 — Vulnerability Scanner

**What it does:**
- GitHub repo URL → clones → scans
- Detects: exposed secrets, outdated deps, missing headers, code vulns
- Risk score 0-100, severity breakdown, fix prompts per vuln
- Downloads: JSON + PDF

**Independence fixes applied:**
- Removed hardcoded `/home/nitesh/Desktop/Projects/root` paths
- `code_analyzer.py` — added `_analyze_typescript` method (was missing vs root)
- `config_checker.py` — fixed .env false positive (skips gitignored files)
- `pdf_generator.py` — all methods inside class (were dead code)

---

## Tool 2 — SQL Injection Tester

**What it does:**
- Manual mode: URL with params → tests it
- Smart Crawl: base URL → auto-discovers params → tests each
- Detects: Error-based, Union-based, Boolean-blind, Time-based
- Real payload files: 60-90 payloads from root portfolio
- Downloads: JSON + PDF

**Payload files (copied from root, trimmed to 60-90 total):**
- `error_based.txt` — ~20 payloads
- `union_based.txt` — ~20 payloads
- `boolean_blind.txt` — ~20 payloads
- `time_based.txt` — ~15 payloads

---

## Tool 3 — XSS Scanner

**What it does:**
- Manual mode + Smart Crawl mode
- Detects: Reflected XSS, Stored XSS patterns
- Real payload files: 40-60 payloads from root portfolio
- False positive fix: control marker verification
- Downloads: JSON + PDF

**Payload files:**
- `reflected.txt` — ~20 payloads
- `bypass.txt` — ~20 payloads
- `stored.txt` — ~10 payloads
- `dom_based.txt` — ~10 payloads

---

## Vulnerable Target App

**Endpoints:**
- `GET /search?q=` — Reflected XSS
- `GET /user?id=` — SQL Injection (SQLite)
- `GET /products?category=` — SQL Injection (SQLite)
- `GET /` — Home with links to all endpoints

**Port:** 8080

---

## Individual Tool Standalone Pages

Each standalone page has:
- Own mini-header (tool name + icon + "Part of SecureScope" badge)
- Own hero section explaining what the tool does
- Full scan form
- Real-time scan terminal
- Results with VulnCards
- Download JSON + PDF
- "← Back to SecureScope" link
- Feels complete if viewed in isolation

---

## Landing Page Design

```
/  (Landing)

[Faint cyan radial glow top-center]

SecureScope
Find vulnerabilities before attackers do.

[Two cards side by side]

┌──────────────────────┐  ┌──────────────────────┐
│  SecureScope         │  │  Individual Tools    │
│  Platform            │  │                      │
│                      │  │  Use each tool as    │
│  Unified dashboard   │  │  a standalone app.   │
│  All 3 tools in      │  │  No platform needed. │
│  one place.          │  │                      │
│                      │  │  → Vuln Scanner      │
│  → Open Platform     │  │  → SQLi Tester       │
│                      │  │  → XSS Scanner       │
└──────────────────────┘  └──────────────────────┘

[Stats row: 3 Tools | 4 Detection Methods | PDF + JSON Reports]
```

---

## Build Order (Phases)

### Phase 1 — Frontend Complete Redesign ← COMPLETE
- [x] Update PLAN.md
- [x] Rewrite index.css — complete dark theme design system
- [x] Rewrite Landing.tsx — selector page with dual mode cards
- [x] Rewrite PlatformHome.tsx — dark dashboard
- [x] Rewrite PlatformNav.tsx — dark navbar
- [x] Rewrite VulnScannerPage.tsx — dark + scan terminal
- [x] Rewrite SQLInjectionPage.tsx — dark + scan terminal
- [x] Rewrite XSSScannerPage.tsx — dark + scan terminal
- [x] Build ScanTerminal.tsx — real-time log component
- [x] Rewrite shared components — dark theme
- [x] Build ToolNav.tsx — standalone tool header
- [x] Build ToolsHome.tsx — individual tools listing
- [x] Build StandaloneVuln.tsx
- [x] Build StandaloneSQLi.tsx
- [x] Build StandaloneXSS.tsx
- [x] Update App.tsx — new routes

### Phase 2 — Payload Upgrade ← COMPLETE
- [x] Copy + trim error_based.txt (20 payloads)
- [x] Copy + trim union_based.txt (20 payloads)
- [x] Copy + trim boolean_blind.txt (20 payloads)
- [x] Copy + trim time_based.txt (15 payloads)
- [x] Copy + trim reflected.txt (20 payloads)
- [x] Copy + trim bypass.txt (20 payloads)
- [x] Copy stored.txt (10 payloads)
- [x] Copy dom_based.txt (10 payloads)
- [x] Update tool2 scanner.py to load from .txt files
- [x] Update tool3 scanner.py to load from .txt files

### Phase 3 — Independence Fix ← COMPLETE
- [x] Remove hardcoded paths from tool1 secret_detector.py
- [x] Remove hardcoded paths from tool1 dependency_checker.py
- [x] Add _analyze_typescript to tool1 code_analyzer.py
- [x] Verify build compiles clean (0 errors)

### Phase 4 — Logo & Favicon ← COMPLETE
- [x] Create SecureScope SVG logo (shield + crosshair, cyan)
- [x] Replace favicon.svg with new logo
- [x] Update index.html title to "SecureScope — Security Testing Platform"
- [x] Add logo component to navbar
- [x] Add logo to landing page badge

### Phase 5 — Vulnerable Target (VulnShop) ← COMPLETE
- [x] Rebuild as "VulnShop" fake e-commerce store
- [x] /search?q= → Reflected XSS
- [x] /product?id= → SQLi error-based
- [x] /category?name= → SQLi union-based
- [x] /user?id= → SQLi boolean-blind
- [x] /review?post_id= → Stored XSS pattern
- [x] /profile?username= → SQLi time-based
- [x] /login → Verbose auth errors
- [x] Clean realistic HTML — looks like a real store
- [x] Realistic seed data (8 products, 4 users, 3 reviews)

### Phase 6 — start.sh Fixes ← COMPLETE
- [x] Kill conflicting ports before starting
- [x] Auto-open browser to localhost:3000 (SecureScope)
- [x] Auto-open browser to localhost:8888 (VulnShop)
- [x] Verify each service started successfully
- [x] Clear status summary table

### Phase 7 — Extra Tools (optional)
- [ ] Security Headers Checker (tool 4)
- [ ] Port Scanner (tool 5)

---

## What Impresses the College Panel

1. **The UI** — Opens and they immediately feel it's real software
2. **Live demo** — Scan vulnerable target, real results in real time
3. **Scan terminal** — They watch it find vulnerabilities live
4. **PDF report** — Professional, looks like a paid product
5. **Dual mode** — "Each tool is also independently deployable as a REST API"
6. **Smart Crawl** — "It automatically discovers all parameters"
7. **Fix recommendations** — "Not just finding bugs, telling you how to fix them"
