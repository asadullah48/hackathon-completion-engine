# Personal AI Employee

**Hackathon 0: Building Autonomous FTEs (Full-Time Equivalents)**

> Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A Digital Full-Time Employee (FTE) powered by **dual AI engines** (Claude Code + OpenAI) and **Obsidian vault** that proactively manages personal and business affairs 24/7. Three watchers (File, Gmail, WhatsApp) detect incoming items, Claude reasons about them, and the HITL approval workflow keeps the human in control of sensitive actions.

[![Tier](https://img.shields.io/badge/tier-gold-ffd700)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![TypeScript](https://img.shields.io/badge/typescript-next.js%2016-black)]()
[![Claude Code](https://img.shields.io/badge/engine-claude%20code-orange)]()
[![OpenAI](https://img.shields.io/badge/engine-openai-412991)]()
[![FastAPI](https://img.shields.io/badge/backend-fastapi-009688)]()

---

## Architecture

```
EXTERNAL SOURCES                    PERCEPTION LAYER (3 Watchers)
  Files in                            File Watcher (Python)
  /mnt/d/AI-Employee-Inbox   --->    monitors every 10s
                                            |
  Gmail (OAuth2)              --->    Gmail Watcher (Google API)
  texcot...@gmail.com                monitors every 2min
                                            |
  WhatsApp Web                --->    WhatsApp Watcher (Playwright)
  Business keyword scanning          monitors every 30s
                                            |
                                            v
                              OBSIDIAN VAULT (Local Markdown)
                              +-------------------------------+
                              | /Inbox       /Needs_Action    |
                              | /Pending_Approval  /Approved  |
                              | /Rejected    /Done            |
                              | /Briefings   /Logs            |
                              | Dashboard.md                  |
                              | Company_Handbook.md           |
                              | Business_Goals.md             |
                              +-------------------------------+
                                            |
                                            v
                              REASONING LAYER (Dual AI Engine)
                              Claude Code CLI -> vault checks
                              Claude API -> vault reasoning
                              OpenAI API -> chat companion
                              Follows Company_Handbook rules
                                            |
                              +-------------+-------------+
                              |                           |
                              v                           v
                        AUTO-EXECUTE              HITL APPROVAL
                        (Low risk)            (Sensitive actions)
                        Update dashboard      Create approval file
                        Categorize files      Wait for human decision
                        Log activities        Execute after approval
                                            |
                                            v
                              ACTION LAYER (Agent Skills + Backend)
                              4 Claude Code agent skills
                              FastAPI backend (dual AI)
                              CEO Briefing generator (data-driven)
                              Orchestrator (process management)
                              Cron scheduling (automated tasks)
```

### Perception -> Reasoning -> Action Flow

1. **Perception**: 3 Watchers (File, Gmail, WhatsApp) detect new items from external sources
2. **Reasoning**: Claude Code reads vault, applies Company_Handbook rules, reasons about actions
3. **Action**: Auto-execute low-risk tasks, HITL-approve sensitive ones, update dashboard, generate briefings

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Claude Code CLI (for orchestration)
- Google Cloud OAuth credentials (for Gmail watcher)
- Playwright + Chromium (for WhatsApp watcher)

### Setup

```bash
# Clone and enter project
git clone https://github.com/asadullah48/hackathon-completion-engine.git
cd hackathon-completion-engine

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (ANTHROPIC_API_KEY + OPENAI_API_KEY)

# Create the drop folder (file watcher monitors this)
mkdir -p /mnt/d/AI-Employee-Inbox
```

### Run Individual Watchers

```bash
# File Watcher -- monitors drop folder
python watchers/file_watcher.py --vault ./vault

# Gmail Watcher -- requires credentials.json + OAuth setup
python watchers/gmail_watcher.py --vault ./vault

# WhatsApp Watcher -- requires Playwright + QR code scan
pip install playwright && playwright install chromium
export DISPLAY=:0  # WSL2 with WSLg
python watchers/whatsapp_watcher.py --vault ./vault
```

### Run the Orchestrator (Full Mode)

```bash
# All watchers + Claude Code + scheduling
python orchestrator.py --gmail --whatsapp

# File watcher only + Claude Code
python orchestrator.py

# Preview mode (no actual actions)
python orchestrator.py --dry-run
```

### Run the Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000/health
# Visit http://localhost:8000/api/vault/status
```

### Run the Frontend

```bash
cd frontend
npm install && npm run dev
# Visit http://localhost:3000
```

### Generate CEO Briefing

```bash
python watchers/ceo_briefing_generator.py --vault ./vault
# Output: vault/Briefings/YYYY-MM-DD-ceo-briefing.md
```

### Setup Cron Jobs

```bash
bash scripts/setup-cron.sh
# Installs: Monday 9AM briefing, 5-min Gmail checks, 6-hour dashboard updates
```

---

## Key Features

### 1. Three Watchers (Perception Layer)

| Watcher | Source | Interval | Auth |
|---------|--------|----------|------|
| **File Watcher** | `/mnt/d/AI-Employee-Inbox` | 10s | None |
| **Gmail Watcher** | Gmail inbox (OAuth2) | 2min | Google OAuth `credentials.json` |
| **WhatsApp Watcher** | WhatsApp Web (Playwright) | 30s | QR code scan |

Each watcher detects relevant items, creates structured action files in `vault/Needs_Action/`, and logs activity to `vault/Logs/`.

### 2. Dual AI Engine (Reasoning Layer)

| Engine | Purpose | Integration |
|--------|---------|-------------|
| **Claude Code CLI** | Vault reasoning & orchestration | `claude --print` via orchestrator |
| **Claude API** | Vault item analysis & triage | `backend/services/claude_service.py` |
| **OpenAI API** | Chat companion with constitutional rules | `backend/services/chatgpt_service.py` |

### 3. Human-in-the-Loop (HITL) Workflow

Sensitive actions create approval files in `vault/Pending_Approval/`. Move files to `vault/Approved/` or `vault/Rejected/` to make decisions. The AI never acts on sensitive matters without human approval.

**Auto-Execute**: Read/categorize files, update dashboard, log activities, generate briefings
**Requires Approval**: External comms, payments >$50, production deploys, data deletion

### 4. Agent Skills (4 Claude Code Skills)

Specialized Claude Code agent skills in `.claude/agents/fte/`:
- **dashboard-updater** -- Scans vault folders, updates Dashboard.md with real-time metrics
- **hitl-approval-manager** -- Creates/processes approval requests, tracks decisions
- **ceo-briefing-generator** -- Weekly executive briefings from real vault data
- **file-processor** -- Categorizes and triages Inbox items by file type

### 5. CEO Briefing (Data-Driven)

Automated weekly briefing generated every Monday at 9 AM:
- Reads real data from `vault/Logs/` (last 7 days)
- Counts items in all vault folders
- Identifies bottlenecks (items >48 hours old)
- Reports watcher health status
- Provides actionable recommendations

### 6. Constitutional AI

Backend middleware enforces safety rules on chat endpoints. Blocked queries get Socratic responses. Flagged queries enter HITL review.

### 7. Orchestrator (Master Process)

`orchestrator.py` coordinates everything:
- Starts/monitors/restarts crashed watchers
- Triggers Claude Code vault checks on interval
- Schedules CEO briefings (Monday 9 AM)
- Graceful shutdown on SIGINT/SIGTERM

### 8. Backend API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Service info + AI engine status |
| `/health` | GET | Health check with dual engine config |
| `/api/chat` | POST | Chat with constitutional filtering |
| `/api/vault/status` | GET | Real-time vault folder counts |
| `/api/vault/triage` | GET | Claude-powered triage recommendations |
| `/api/vault/reason` | POST | Analyze specific vault items with Claude |
| `/api/vault/needs-action` | GET | List items awaiting action |
| `/api/conversations/{id}` | GET | Conversation history |

---

## Vault Structure

```
vault/
  Dashboard.md           # Real-time business snapshot (auto-updated)
  Company_Handbook.md    # Rules of engagement (v2.0.0)
  Business_Goals.md      # Strategic objectives and KPIs
  Inbox/                 # New items to triage
  Needs_Action/          # Items requiring processing
  Pending_Approval/      # HITL: awaiting human decision
  Approved/              # Human-approved actions
  Rejected/              # Human-rejected actions
  Done/                  # Completed items
  Briefings/             # CEO briefing output
  Logs/                  # Daily JSON activity logs
  Conversation_Logs/     # Chat history
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Reasoning** | Claude Code CLI + Claude API (Anthropic) |
| **Chat** | OpenAI API + Constitutional AI middleware |
| **Memory/GUI** | Obsidian vault (local Markdown) |
| **Perception** | 3 Python watchers (file, Gmail, WhatsApp) |
| **Backend** | Python FastAPI + Uvicorn |
| **Frontend** | Next.js 16 + TypeScript + Tailwind CSS |
| **Browser Automation** | Playwright (WhatsApp Web) |
| **Scheduling** | Python `schedule` + cron |
| **Orchestration** | Python orchestrator with process management |
| **Deployment** | Render (backend) + Vercel (frontend) |

---

## Live Deployment

| Service | URL |
|---------|-----|
| **Backend API (Render)** | [https://personal-ai-employee-backend.onrender.com](https://personal-ai-employee-backend.onrender.com) |
| **Frontend (Vercel)** | [https://frontend-three-kappa-64.vercel.app](https://frontend-three-kappa-64.vercel.app) |

### Quick Verify

```bash
# Health check (dual AI engines)
curl https://personal-ai-employee-backend.onrender.com/health

# Vault status (real-time folder counts)
curl https://personal-ai-employee-backend.onrender.com/api/vault/status

# Service info
curl https://personal-ai-employee-backend.onrender.com/
```

### Deploy from Source

**Render (Backend)**:
1. Push to GitHub
2. Connect repo to Render → auto-detects `render.yaml`
3. Set `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` as env vars

**Vercel (Frontend)**:
```bash
cd frontend
vercel --prod -e NEXT_PUBLIC_API_URL=https://personal-ai-employee-backend.onrender.com
```

---

## Tier Compliance

### Bronze Tier -- COMPLETE

- [x] Obsidian vault with Dashboard.md (real-time metrics)
- [x] Company_Handbook.md (v2.0.0 with decision framework)
- [x] One working Watcher script (file watcher)
- [x] Claude Code reading/writing vault (orchestrator + API)
- [x] Folder structure: /Inbox, /Needs_Action, /Done + 6 more
- [x] AI functionality as Agent Skills (4 skills)

### Silver Tier -- COMPLETE

- [x] Three Watcher scripts (File + Gmail + WhatsApp)
- [x] Claude reasoning loop (orchestrator triggers `claude --print`)
- [x] HITL approval workflow (Pending_Approval folder-based)
- [x] Basic scheduling (cron + Python schedule)
- [x] Agent Skills with YAML frontmatter (executable format)

### Gold Tier -- COMPLETE

- [x] CEO Briefing with real data (data-driven from vault/Logs)
- [x] Audit logging (JSON logs in vault/Logs/)
- [x] Dual AI engine (OpenAI chat + Claude reasoning)
- [x] Error recovery (orchestrator restarts crashed watchers)
- [x] Deployment ready (render.yaml + Vercel)

---

## Hackathon Submission

| Deliverable | Link / Status |
|-------------|---------------|
| **GitHub Repository** | [asadullah48/hackathon-completion-engine](https://github.com/asadullah48/hackathon-completion-engine) |
| **Live Backend** | [personal-ai-employee-backend.onrender.com](https://personal-ai-employee-backend.onrender.com) |
| **Live Frontend** | [frontend-three-kappa-64.vercel.app](https://frontend-three-kappa-64.vercel.app) |
| **Demo Video** | _TODO: Add YouTube/Loom link_ |
| **Tier Declaration** | Gold |
| **Architecture** | See diagram above |
| **Security** | Credentials in `.env` (gitignored); HITL for sensitive actions; audit logging |

---

## Author

**Asadullah Shafique**
- GitHub: [@asadullah48](https://github.com/asadullah48)
- GIAIC Roll: 00458550
- Program: Panaversity Hackathon II

---

## License

MIT License - See [LICENSE](./LICENSE) file for details

---

**Built as an Autonomous Digital FTE -- Your life and business on autopilot.**
