# H4.5 SPECIFICATION: DISCORD BOT INTEGRATION
**TodoMaster AI — Discord-Native Task Management**

---

## PROJECT OVERVIEW

**Project Name:** H4.5 — Discord Bot Integration  
**Developer:** Asadullah Shafique (@asadullah48)  
**Base Project:** H4 Cloud-Native Todo App (Platinum Tier)  
**GitHub:** https://github.com/asadullah48/hackathon-completion-engine  
**Discord Server:** https://discord.gg/xUeg2VSV  
**Estimated Time:** 12–16 hours (4 sessions × 3–4 hours)  
**Start Date:** February 2026  
**Target:** Working Discord bot deployed on existing K8s cluster

---

## MISSION STATEMENT

Build **TodoMaster AI** — a Discord bot that connects to the existing H4 todo app backend, enabling users to manage todos, collaborate in teams, and leverage Constitutional AI directly from Discord. Deploy as a new microservice on the existing Kubernetes cluster alongside the current backend, frontend, notification service, Kafka, and Prometheus stack.

**Success Criteria:** Bot responds to slash commands, creates/manages todos via the existing FastAPI backend, publishes events to Kafka, and enforces Constitutional AI — all running in K8s.

---

## ARCHITECTURE

### How the Bot Fits into H4

```
┌─────────────────────────────────────────────────────┐
│                 KUBERNETES CLUSTER                    │
│                  (todo-app namespace)                 │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Frontend  │  │ Backend  │  │  Discord Bot      │   │
│  │ Next.js   │  │ FastAPI  │  │  discord.py       │   │
│  │ (existing)│  │(existing)│  │  (NEW SERVICE)    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────────────┘   │
│       │              │              │                  │
│       └──────┬───────┘              │                  │
│              │                      │                  │
│       ┌──────▼──────┐     ┌────────▼────────┐        │
│       │ PostgreSQL   │     │ Discord API      │        │
│       │ (existing)   │     │ (external)       │        │
│       └──────────────┘     └─────────────────┘        │
│                                                       │
│  ┌──────────┐  ┌──────┐  ┌────────────┐             │
│  │  Kafka   │  │Redis │  │ Prometheus │              │
│  │(existing)│  │(exist)│  │ (existing) │              │
│  └──────────┘  └──────┘  └────────────┘              │
└───────────────────────────────────────────────────────┘
```

### Key Design Decision: Bot as API Client

The Discord bot does NOT duplicate business logic. It calls the existing FastAPI backend via internal K8s service URL (`http://todo-app-backend:8000`). This means:

- All 149 tests still validate core logic
- Constitutional AI enforcement stays in backend
- Kafka events fire automatically from existing endpoints
- Bot is a thin client — slash commands → API calls → rich Discord responses

---

## BOT IDENTITY

```yaml
Bot Name: TodoMaster AI
Bot Prefix: / (slash commands only, no message prefix)
Bot Avatar: Todo checkmark with AI sparkle
Bot Status: "Managing X todos across Y servers"
Bot Color: #5865F2 (Discord Blurple)
```

---

## SESSION BREAKDOWN

### Session 1: Bot Foundation (3–4 hours)

**Goal:** Working bot with core slash commands connected to existing backend.

**Deliverables:**

1. **Discord Developer Portal Setup**
   - Create application at https://discord.com/developers
   - Generate bot token
   - Configure OAuth2 scopes: `bot`, `applications.commands`
   - Bot permissions: Send Messages, Embed Links, Add Reactions, Use Slash Commands, Read Message History, Manage Channels
   - Store token in K8s Secret

2. **Bot Service (Python/discord.py)**
   ```
   services/discord-bot/
   ├── Dockerfile
   ├── requirements.txt
   ├── bot/
   │   ├── __init__.py
   │   ├── main.py              # Bot entry point
   │   ├── config.py            # Settings from env/configmap
   │   ├── api_client.py        # HTTP client for FastAPI backend
   │   ├── cogs/
   │   │   ├── __init__.py
   │   │   ├── todo.py          # /todo create, list, complete, delete, show
   │   │   ├── team.py          # /team create, invite, list
   │   │   └── help.py          # /help command
   │   ├── embeds/
   │   │   ├── __init__.py
   │   │   └── todo_embed.py    # Rich embed builders for todo display
   │   └── utils/
   │       ├── __init__.py
   │       └── pagination.py    # Paginated list views
   └── tests/
       ├── test_api_client.py
       └── test_commands.py
   ```

3. **Core Slash Commands (Phase 1)**

   | Command | Description | API Endpoint |
   |---------|-------------|--------------|
   | `/todo create <title> [deadline] [priority]` | Create a todo | `POST /api/todos` |
   | `/todo list [filter]` | List todos (all/active/completed) | `GET /api/todos` |
   | `/todo complete <id>` | Mark todo done | `PATCH /api/todos/{id}` |
   | `/todo delete <id>` | Delete a todo | `DELETE /api/todos/{id}` |
   | `/todo show <id>` | Show todo details | `GET /api/todos/{id}` |
   | `/help` | Show all commands | — |

4. **API Client (Internal K8s Communication)**
   ```python
   # bot/api_client.py
   class TodoAPIClient:
       def __init__(self):
           # Internal K8s service URL — no external exposure needed
           self.base_url = os.getenv("BACKEND_URL", "http://todo-app-backend:8000")
       
       async def create_todo(self, title, deadline=None, priority="medium"):
           async with aiohttp.ClientSession() as session:
               resp = await session.post(f"{self.base_url}/api/todos", json={...})
               return await resp.json()
   ```

5. **Rich Embeds for Todo Display**
   ```
   ┌─────────────────────────────────┐
   │ ✅ Todo #42                      │
   │ ─────────────────────────        │
   │ 📝 Review PR for auth module    │
   │ 📅 Due: Feb 15, 2026 2:00 PM   │
   │ 🔴 Priority: High               │
   │ 🏷️ Category: Work               │
   │ 👤 Assigned: @asadullah          │
   │ ─────────────────────────        │
   │ Created: 2 hours ago             │
   └─────────────────────────────────┘
   ```

6. **K8s Deployment**
   ```yaml
   # k8s/discord-bot-deployment.yaml
   - New Deployment (1 replica, no Dapr sidecar needed for MVP)
   - ConfigMap: BACKEND_URL, BOT_PREFIX
   - Secret: DISCORD_BOT_TOKEN
   - No Service needed (bot connects outbound to Discord API)
   ```

7. **Docker Image**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY bot/ ./bot/
   CMD ["python", "-m", "bot.main"]
   ```

**Validation:**
- [ ] Bot appears online in Discord server
- [ ] `/todo create "Test task"` creates todo and returns embed
- [ ] `/todo list` shows paginated list
- [ ] `/todo complete <id>` marks done
- [ ] Bot running as K8s pod in todo-app namespace
- [ ] Backend API calls work via internal service URL

---

### Session 2: Advanced Features & OAuth (3–4 hours)

**Goal:** User accounts, interactive components, and team features.

**Deliverables:**

1. **User Account Linking**
   - Discord user ID → App user mapping table
   - `/account link` — generates one-time code, user enters on web app
   - `/account status` — shows linked account info
   - Unlinked users get guest access (limited to 10 todos)

2. **Interactive Components**
   ```
   /todo list
   ┌─────────────────────────────────┐
   │ 📋 Your Todos (3 active)        │
   │                                  │
   │ 1. ⬜ Review PR          🔴 High │
   │ 2. ⬜ Write tests        🟡 Med  │
   │ 3. ✅ Fix bug            🟢 Low  │
   │                                  │
   │ [✅ Complete] [🗑️ Delete] [📝 Edit] │
   │ [◀ Prev]              [Next ▶]  │
   └─────────────────────────────────┘
   ```
   - Buttons: Complete, Delete, Edit (opens modal)
   - Select menus: Change priority, assign member
   - Modals: Edit todo title/description/deadline

3. **Team Commands**

   | Command | Description | API Endpoint |
   |---------|-------------|--------------|
   | `/team create <name>` | Create team from server | `POST /api/teams` |
   | `/team list` | Show teams | `GET /api/teams` |
   | `/team assign <todo_id> @user` | Assign todo | `PATCH /api/todos/{id}` |
   | `/todo stats` | Team productivity stats | `GET /api/todos` (aggregated) |

4. **Channel → Project Mapping**
   ```
   Discord Server  →  Todo Team
   #general        →  Default project
   #frontend       →  Frontend project
   #backend        →  Backend project
   ```
   - Todos created in #frontend auto-tagged "frontend"
   - `/todo list` in #frontend shows only frontend todos

5. **Webhook Notifications (Outbound)**
   - New Kafka consumer in notification service
   - Listen to `todo-events` topic
   - On todo.created → post to configured channel
   - On todo.completed → celebration message
   - On deadline approaching → reminder DM

**Validation:**
- [ ] Interactive buttons work (complete/delete from embed)
- [ ] Modals open for editing
- [ ] `/team create` and `/team assign` work
- [ ] Channel-based filtering works
- [ ] Kafka events trigger Discord notifications

---

### Session 3: AI Features & Constitutional AI (3–4 hours)

**Goal:** Natural language parsing, smart suggestions, Constitutional AI enforcement in Discord.

**Deliverables:**

1. **Natural Language Todo Creation**
   ```
   User: "Remind me to review PR tomorrow at 2pm"
   Bot: ✅ Created todo "Review PR"
        📅 Deadline: Tomorrow 2:00 PM
        📊 Priority: Medium (auto-detected)
        🏷️ Category: Work (auto-detected)
        
        [✅ Confirm] [✏️ Edit] [❌ Cancel]
   ```
   - Parse natural language → structured todo
   - Use existing NLP parsing from H3 backend
   - Show preview before confirming

2. **Constitutional AI in Discord**
   ```
   User: /todo create "Write my essay for English class"
   Bot: ⚠️ This request was flagged by our AI safety system.
        
        Reason: Potential academic dishonesty
        
        TodoMaster AI helps you manage YOUR tasks,
        not do your homework for you! 📚
        
        💡 Try instead: "Study for English essay" or
        "Outline key points for English essay"
   ```
   - All todo creation routed through existing Constitutional AI
   - Block patterns enforced (7 BLOCK + 5 FLAG)
   - Friendly, non-preachy messages (match H3 style)
   - Admin override for server owners

3. **Smart Suggestions via Discord**
   ```
   Bot DM: 💡 I noticed you created "Exercise" 5 times
           Would you like to make this recurring?
           
           [🔁 Make Daily] [🔁 Make Weekly] [❌ Dismiss]
   ```
   - Recurring pattern detection → suggest automation
   - Overdue todo reminders → daily DM digest
   - Productivity tips based on completion patterns

4. **AI Suggestion Command**

   | Command | Description |
   |---------|-------------|
   | `/todo suggest` | Get AI-powered task suggestions |
   | `/todo parse <text>` | Parse natural language into todo |
   | `/todo recurring <pattern>` | Create recurring todo |

**Validation:**
- [ ] Natural language parsing creates correct todos
- [ ] Constitutional AI blocks inappropriate requests
- [ ] Smart suggestions appear for recurring patterns
- [ ] `/todo suggest` returns relevant suggestions
- [ ] Friendly error messages (not preachy)

---

### Session 4: Polish, Testing & Launch Prep (3–4 hours)

**Goal:** Production hardening, comprehensive testing, documentation, beta launch.

**Deliverables:**

1. **Error Handling & Resilience**
   - Graceful degradation if backend is down
   - Rate limiting per user (prevent spam)
   - Timeout handling for API calls
   - Retry logic with exponential backoff
   - User-friendly error messages

2. **Testing Suite**
   ```
   tests/
   ├── test_api_client.py        # Backend communication
   ├── test_commands.py           # Slash command parsing
   ├── test_embeds.py             # Embed generation
   ├── test_constitutional.py     # AI safety enforcement
   ├── test_pagination.py         # List pagination
   └── test_integration.py        # End-to-end flows
   ```
   - Target: 30+ tests for bot service
   - Mock Discord API for unit tests
   - Integration tests against real backend

3. **K8s Production Config**
   ```yaml
   resources:
     requests:
       memory: "128Mi"
       cpu: "100m"
     limits:
       memory: "256Mi"
       cpu: "250m"
   livenessProbe:
     httpGet:
       path: /health  # Simple health endpoint
       port: 8080
   ```
   - Health check endpoint
   - Resource limits
   - Restart policy
   - Prometheus metrics (commands/sec, latency, errors)

4. **Bot Landing Message**
   ```
   👋 Welcome to TodoMaster AI!
   
   The ONLY todo bot with Constitutional AI.
   
   Quick Start:
   • /todo create "Your first task"
   • /todo list
   • /todo help
   
   ⚡ Powered by AI | 🛡️ Constitutional AI Protected
   ```

5. **Documentation**
   - `docs/discord-bot.md` — Setup guide
   - `docs/discord-commands.md` — Full command reference
   - Bot invite link with correct permissions
   - Privacy policy (what data bot accesses)

6. **Beta Launch in Your Server**
   - Deploy to K8s cluster
   - Invite bot to https://discord.gg/xUeg2VSV
   - Create channels: #todo-feed, #celebrations, #reminders
   - Test all commands with real users
   - Gather feedback

**Validation:**
- [ ] 30+ tests passing
- [ ] Bot handles backend downtime gracefully
- [ ] Rate limiting works
- [ ] Health check responding
- [ ] Prometheus metrics exposed
- [ ] Documentation complete
- [ ] Bot live in Discord server

---

## TECH STACK

| Component | Technology | Version |
|-----------|-----------|---------|
| Bot Framework | discord.py | 2.3+ |
| HTTP Client | aiohttp | 3.9+ |
| Language | Python | 3.11 |
| Container | Docker | Multi-stage |
| Orchestration | Kubernetes | Existing cluster |
| Backend API | FastAPI | Existing |
| Database | PostgreSQL | Existing |
| Events | Kafka | Existing (Strimzi) |
| Cache | Redis | Existing |
| Monitoring | Prometheus | Existing |

---

## MONETIZATION TIERS (Post-Launch)

### Free Tier
- 50 todos/month per server
- 1 team (5 members)
- Basic slash commands
- Constitutional AI (always free)

### Pro ($9/month per user)
- Unlimited todos
- 5 teams (50 members each)
- AI suggestions (100/month)
- Calendar sync (1 provider)
- Full Discord bot features

### Team ($29/month)
- Everything in Pro
- 20 teams (unlimited members)
- Unlimited AI suggestions
- Admin dashboard
- Priority support

### Discord Bot Premium ($5/month per server)
- Unlimited todos
- AI suggestions in Discord
- Custom commands
- Webhook integrations
- Analytics dashboard

---

## COMPETITIVE ADVANTAGES

1. **Constitutional AI** — UNIQUE. No competitor has ethical AI enforcement in a todo bot.
2. **Discord-First** — Most todo apps treat Discord as an afterthought.
3. **Production Infrastructure** — K8s, Kafka, Prometheus from day one.
4. **149+ Tests** — Battle-tested backend.
5. **Event-Driven** — Real-time notifications via Kafka → Discord.

---

## SUCCESS METRICS

### Beta (Week 1–2)
- Bot online 99%+ uptime
- All slash commands working
- 0 Constitutional AI bypasses
- Positive feedback from beta users

### Launch (Month 1)
- 100 Discord servers
- 1,000 active users
- 10,000 todos created
- 4.5+ star rating

### Growth (Month 3–6)
- 1,000 Discord servers
- 10,000 active users
- 100 paying customers
- $500 MRR

### Scale (Year 1)
- 10,000 Discord servers
- 100,000 active users
- $10K MRR
- Featured in Discord Bot Directory

---

## RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Discord API rate limits | Medium | Implement rate limiting, queue commands |
| Backend downtime | High | Graceful degradation, cached responses |
| Bot token leak | Critical | K8s Secret, never in code/git |
| User abuse | Medium | Rate limits, Constitutional AI, admin controls |
| Scaling issues | Low | K8s HPA, stateless bot design |

---

## CLAUDE CODE SESSION PROMPTS

### Session 1 Prompt (Paste into Claude Code)
```
H4.5 Session 1: Discord Bot Foundation

Project: /mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/
GitHub: https://github.com/asadullah48/hackathon-completion-engine
Existing: K8s cluster running with backend, frontend, PostgreSQL, Redis, Kafka, Prometheus

TASK: Create Discord bot microservice that connects to existing FastAPI backend.

1. Create services/discord-bot/ directory structure
2. Implement bot with discord.py (slash commands)
3. Build API client for internal K8s backend communication
4. Core commands: /todo create, list, complete, delete, show, /help
5. Rich embed builders for todo display
6. Dockerfile (Python 3.11 slim, multi-stage)
7. K8s manifests: Deployment, ConfigMap, Secret placeholder
8. Unit tests for API client and command parsing
9. Deploy to existing K8s cluster (todo-app namespace)

IMPORTANT:
- Bot calls existing backend at http://todo-app-backend:8000
- Do NOT duplicate business logic
- Use existing Constitutional AI from backend
- Store Discord token in K8s Secret
- No Dapr sidecar needed for bot (direct HTTP to backend)

VALIDATION:
- Bot pod Running in todo-app namespace
- /todo create works and returns embed
- /todo list shows paginated results
- Unit tests pass
- Git commit with session summary
```

---

**Specification Version:** 1.0  
**Last Updated:** February 12, 2026  
**Status:** Ready for Implementation  
**Prerequisite:** H4 Platinum Tier Complete ✅
