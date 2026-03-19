# Personal AI Employee

**Hackathon 0: Building Autonomous FTEs (Full-Time Equivalents)**

> Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A Digital Full-Time Employee (FTE) powered by Claude Code and Obsidian that proactively manages personal and business affairs 24/7. File watchers detect new items, Claude Code reasons about them, and the HITL approval workflow keeps the human in control of sensitive actions.

[![Tier](https://img.shields.io/badge/tier-bronze-cd7f32)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![TypeScript](https://img.shields.io/badge/typescript-next.js%2016-black)]()
[![Claude Code](https://img.shields.io/badge/engine-claude%20code-orange)]()

---

## Architecture

```
EXTERNAL SOURCES                    PERCEPTION LAYER
  Files dropped in                    File Watcher (Python)
  /mnt/d/AI-Employee-Inbox   --->    monitors every 10s
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
                              REASONING LAYER (Claude Code)
                              Read -> Think -> Plan -> Act
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
                              ACTION LAYER (MCP + Backend)
                              FastAPI backend (port 8000)
                              CEO Briefing generator
                              Orchestrator coordination
```

### Perception -> Reasoning -> Action Flow

1. **Perception**: File Watcher detects new files in the drop folder
2. **Reasoning**: Claude Code reads vault, applies Company_Handbook rules, creates plans
3. **Action**: Auto-execute low-risk tasks, HITL-approve sensitive ones, update dashboard

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Claude Code CLI (for full orchestration)

### Setup

```bash
# Clone and enter project
git clone https://github.com/asadullah48/hackathon-completion-engine.git
cd hackathon-completion-engine

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Create the drop folder (file watcher monitors this)
mkdir -p /mnt/d/AI-Employee-Inbox
```

### Run the File Watcher

```bash
python watchers/file_watcher.py --vault ./vault
```

Drop a test file and watch it get processed:
```bash
echo "Test invoice from Client A" > /mnt/d/AI-Employee-Inbox/invoice.txt
# Check vault/Needs_Action/ -- a new action item appears
```

### Run the Orchestrator (Full Mode)

```bash
# Full orchestration (file watcher + Claude Code + scheduling)
python orchestrator.py

# Preview mode (no actual actions)
python orchestrator.py --dry-run

# Without Claude Code CLI
python orchestrator.py --no-claude
```

### Run the Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000/health
```

### Run the Frontend

```bash
cd frontend
npm install && npm run dev
# Visit http://localhost:3000
```

---

## Key Features

### 1. File System Watcher
Monitors `/mnt/d/AI-Employee-Inbox` every 10 seconds. Categorizes files (document, code, data, image, video, archive) and creates structured action items in the vault.

### 2. Human-in-the-Loop (HITL) Workflow
Sensitive actions create approval files in `vault/Pending_Approval/`. Move files to `vault/Approved/` or `vault/Rejected/` to make decisions. The AI never acts on sensitive matters without human approval.

### 3. Claude Code as the Brain
CLAUDE.md at the project root tells Claude Code how to operate as the AI Employee. It reads the vault, follows Company_Handbook rules, processes items, and updates the dashboard.

### 4. Agent Skills
Four specialized Claude Code agent skills in `.claude/agents/fte/`:
- **dashboard-updater** -- Scans vault folders, updates Dashboard.md metrics
- **hitl-approval-manager** -- Creates/processes approval requests
- **ceo-briefing-generator** -- Weekly executive briefings from logs and metrics
- **file-processor** -- Categorizes and triages Inbox items

### 5. CEO Briefing
Automated weekly briefing generated every Monday at 9 AM, summarizing completed tasks, bottlenecks, financial metrics, and proactive suggestions.

### 6. Constitutional AI
Backend middleware enforces safety rules. Blocked queries get Socratic responses. Flagged queries enter HITL review.

---

## Vault Structure

```
vault/
  Dashboard.md           # Real-time business snapshot
  Company_Handbook.md    # Rules of engagement
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
| **Brain** | Claude Code (reasoning engine) |
| **Memory/GUI** | Obsidian vault (local Markdown) |
| **Perception** | Python file watcher (watchers/) |
| **Backend** | Python FastAPI + Uvicorn |
| **Frontend** | Next.js 16 + TypeScript + Tailwind CSS |
| **AI Chat** | OpenAI API + Constitutional AI middleware |
| **Orchestration** | Python orchestrator with schedule library |
| **Deployment** | Render (backend + frontend) |

---

## Deployment

### Render

The project includes a `render.yaml` Blueprint for one-click deployment:

1. Push to GitHub
2. Connect repo to Render
3. Render auto-detects `render.yaml` and deploys both services
4. Set `OPENAI_API_KEY` in Render environment variables

**Backend**: `https://personal-ai-employee-backend.onrender.com`
**Frontend**: `https://personal-ai-employee-frontend.onrender.com`

---

## Background: Hackathon Progression

This project evolved through 5 progressive hackathons:

| Hackathon | Project | What Was Built | Tier |
|-----------|---------|---------------|------|
| **H0** | Personal AI Employee | File watcher, HITL workflow, vault, agent skills | Bronze |
| **H1** | Course Companion | FastAPI backend, Constitutional AI filter | Silver |
| **H2** | AI-Powered Todo | Spec-driven development, CRUD with constitution | Silver |
| **H3** | Advanced Todo | Event-driven (Kafka, Dapr), team collaboration | Gold |
| **H4** | Cloud-Native | Full Kubernetes cluster (14 manifests), CI/CD | Platinum |
| **H4.5** | Discord Bot | TodoMaster AI with 6 slash commands | Extended |

---

## Hackathon Submission

| Deliverable | Link / Status |
|-------------|---------------|
| **Submission Form** | [Google Form](https://forms.gle/JR9T1SJq5rmQyGkGA) |
| **GitHub Repository** | [asadullah48/hackathon-completion-engine](https://github.com/asadullah48/hackathon-completion-engine) |
| **Demo Video** | _TODO: Add YouTube/Loom link_ |
| **Tier Declaration** | Bronze |
| **Architecture** | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| **Security** | Credentials in `.env` (gitignored); K8s Secrets for cloud; HITL for sensitive actions |

### Judging Criteria Alignment

| Criteria | Weight | How This Project Addresses It |
|----------|--------|-------------------------------|
| **Functionality** | 30% | File watcher + HITL workflow + vault dashboard + CEO briefing + agent skills + orchestrator |
| **Innovation** | 25% | Claude Code as autonomous FTE brain, vault-based HITL, agent skill architecture |
| **Practicality** | 20% | Actually usable for daily file triage, Render deployment for cloud access |
| **Security** | 15% | HITL approval workflow, .env credentials, constitutional AI filtering, audit logging |
| **Documentation** | 10% | README, CLAUDE.md, ARCHITECTURE.md, Company_Handbook, agent skill docs |

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
