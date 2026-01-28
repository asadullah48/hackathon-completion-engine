# H2: AI-Powered Todo App

**Zero-Backend-LLM with Constitutional Compliance**

[![Status](https://img.shields.io/badge/status-silver%20tier-silver)]()
[![Backend Tests](https://img.shields.io/badge/backend%20tests-67%20passing-brightgreen)]()
[![Frontend Tests](https://img.shields.io/badge/frontend%20tests-61%20passing-brightgreen)]()
[![TypeScript](https://img.shields.io/badge/typescript-5.3-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

> Constitutional AI todo app that prevents harmful task creation while enabling intelligent natural language parsing. All AI logic runs client-side (Zero-Backend-LLM architecture).

---

## Overview

H2 Todo is a spec-driven AI-powered task management application that demonstrates:

- **Constitutional AI Enforcement**: Prevents creation of harmful, illegal, or academically dishonest tasks
- **Zero-Backend-LLM Architecture**: AI parsing runs entirely in the browser (no backend AI calls)
- **Human-in-the-Loop (HITL)**: Flagged content requires human review before proceeding
- **Natural Language Processing**: Users type naturally, AI extracts structure

### Key Innovation

Unlike traditional todo apps, H2 Todo acts as an ethical gatekeeper:

```
User: "Do my homework assignment"
App:  BLOCKED - Academic dishonesty detected

User: "Study chapter 5 for Friday exam"
App:  ALLOWED - Legitimate study task created
```

---

## Features

### Constitutional AI Enforcement
- [x] 7 BLOCK patterns (academic dishonesty, illegal activities, harmful content)
- [x] 5 FLAG patterns (suspicious patterns requiring HITL review)
- [x] Real-time validation (frontend + backend)
- [x] Vault logging for audit trail
- [x] HITL approval queue for flagged todos

### AI-Powered Parsing
- [x] Natural language to structured todo conversion
- [x] Smart category detection (work, personal, study, health, other)
- [x] Priority inference (high, medium, low)
- [x] Deadline extraction ("tomorrow", "next Friday", "in 3 days")
- [x] Confidence scoring

### Full CRUD Operations
- [x] Create todos with constitutional validation
- [x] Read with filters (category, status, priority, search)
- [x] Update with re-validation
- [x] Delete with confirmation
- [x] Statistics dashboard

### Professional UI
- [x] Responsive design (mobile + desktop)
- [x] List and grid view toggle
- [x] Multi-select filters
- [x] Debounced search
- [x] Toast notifications
- [x] Slide-in edit modal
- [x] Constitutional guard alerts (red/yellow/green)

---

## Architecture

### Zero-Backend-LLM Design

```
                        +------------------+
                        |   FRONTEND       |
                        |   (Next.js)      |
                        |                  |
User Input  ───────────>│  AI Parser       │
"Buy milk tomorrow"     │  (OpenAI API)    │
                        │                  │
                        │  Constitutional  │
                        │  Filter          │
                        +--------│---------+
                                 │
                        +--------v---------+
                        |   BACKEND        |
                        |   (FastAPI)      |
                        |                  |
                        │  Constitutional  │
                        │  Validator       │
                        │  (Double-check)  │
                        │                  │
                        │  SQLite DB       │
                        +------------------+
```

**Why Zero-Backend-LLM?**
- Reduced latency (AI runs in browser)
- Lower server costs
- Privacy (raw prompts don't hit backend)
- Offline-capable (with mock AI fallback)

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone repository
git clone https://github.com/asadullah48/hackathon-completion-engine.git
cd hackathon-completion-engine/hackathons/h2-todo-spec-driven

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend
uvicorn main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install

# Start frontend
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Environment Variables

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_API_KEY=your_key_here  # Optional, uses mock if blank
```

---

## Constitutional Rules

### BLOCKED (Prohibited)

| Category | Example | Reason |
|----------|---------|--------|
| Academic Dishonesty | "Do my homework" | Delegating academic work |
| Academic Dishonesty | "Write my essay" | Academic fraud |
| Academic Dishonesty | "Plagiarize this" | Copying others' work |
| Illegal Activity | "Hack into server" | Unauthorized access |
| Illegal Activity | "Create fake ID" | Forgery |
| Illegal Activity | "Steal passwords" | Theft |
| Harmful Content | "Harass competitor" | Harassment |
| Harmful Content | "Spread misinformation" | Disinformation |

### FLAGGED (Requires Review)

| Pattern | Example | Concern |
|---------|---------|---------|
| Urgent + Assignment | "Urgent: finish assignment in 1 hour" | Last-minute academic pressure |
| Exam Tomorrow | "Exam tomorrow, need help" | Time pressure may lead to shortcuts |
| Complete Before Deadline | "Complete assignment before midnight" | Academic integrity concern |

### ALLOWED (Legitimate)

| Example | Category |
|---------|----------|
| "Study for biology exam" | study |
| "Prepare client presentation" | work |
| "Exercise for 30 minutes" | health |
| "Buy groceries" | personal |
| "Read chapter 5" | study |
| "Practice coding problems" | study |

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/todos` | Create todo (with constitutional check) |
| `GET` | `/api/todos` | List todos (with filters) |
| `GET` | `/api/todos/{id}` | Get single todo |
| `PUT` | `/api/todos/{id}` | Update todo |
| `DELETE` | `/api/todos/{id}` | Delete todo |
| `GET` | `/api/stats` | Get statistics |
| `GET` | `/health` | Health check |

### Create Todo

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Study biology chapter 5"}'
```

Response (ALLOWED):
```json
{
  "id": "uuid",
  "title": "Study biology chapter 5",
  "category": "study",
  "priority": "medium",
  "status": "pending",
  "constitutional_check": {
    "passed": true,
    "decision": "allow"
  }
}
```

Response (BLOCKED):
```json
{
  "detail": {
    "error": "constitutional_violation",
    "message": "Academic dishonesty detected",
    "decision": "block"
  }
}
```

### Filter Todos

```bash
# By category
curl "http://localhost:8000/api/todos?category=work"

# By status
curl "http://localhost:8000/api/todos?status=completed"

# Search
curl "http://localhost:8000/api/todos?search=biology"

# Combined
curl "http://localhost:8000/api/todos?category=study&priority=high"
```

---

## Testing

### Backend Tests (67 tests)

```bash
cd backend
python -m pytest ../tests/ -v
```

Test categories:
- Constitutional patterns (27 tests)
- CRUD operations (22 tests)
- Model validation (18 tests)

### Frontend Tests (61 tests)

```bash
cd frontend
npm test
```

Test categories:
- Constitutional filter (30 tests)
- AI parser (31 tests)

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| SQLAlchemy | ORM for SQLite |
| Pydantic | Data validation |
| pytest | Testing |
| uvicorn | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| Next.js 14 | React framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Zustand | State management |
| Lucide React | Icons |
| date-fns | Date formatting |

---

## UI Components

| Component | Description |
|-----------|-------------|
| `CreateTodoForm` | AI-powered natural language input with constitutional guard |
| `TodoList` | Sortable, groupable todo list with grid/list view |
| `TodoItem` | Individual todo with status toggle, edit, delete |
| `TodoFilters` | Multi-select filters with debounced search |
| `TodoStats` | Dashboard with completion rate, category breakdown |
| `EditTodoModal` | Slide-in panel for editing with re-validation |
| `ConstitutionalAlert` | Red (blocked), yellow (flagged) alerts |

---

## Project Structure

```
h2-todo-spec-driven/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── routers/
│   │   └── todos.py         # API endpoints
│   ├── models/
│   │   └── todo.py          # SQLAlchemy model
│   ├── schemas/
│   │   └── todo.py          # Pydantic schemas
│   ├── services/
│   │   └── constitutional_validator.py
│   └── database.py          # DB connection
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Main page
│   │   └── globals.css      # Tailwind styles
│   ├── components/
│   │   ├── CreateTodoForm.tsx
│   │   ├── TodoList.tsx
│   │   ├── TodoItem.tsx
│   │   ├── TodoFilters.tsx
│   │   ├── TodoStats.tsx
│   │   ├── EditTodoModal.tsx
│   │   └── ConstitutionalAlert.tsx
│   ├── lib/
│   │   ├── aiTodoParser.ts
│   │   ├── constitutionalTodoFilter.ts
│   │   ├── openaiClient.ts
│   │   ├── api.ts
│   │   ├── store.ts
│   │   ├── types.ts
│   │   └── utils.ts
│   └── __tests__/
├── tests/
│   ├── test_constitutional_todos.py
│   ├── test_crud_operations.py
│   └── test_models.py
├── vault/
│   ├── Constitutional_Rules/
│   │   └── todo-rules.md
│   ├── Pending_Approval/     # HITL queue
│   └── Logs/                 # Audit trail
└── README.md
```

---

## Future Enhancements (Gold Tier)

- [ ] OAuth authentication
- [ ] Cloud deployment (Vercel + Railway)
- [ ] Multi-user support
- [ ] Todo sharing/collaboration
- [ ] Calendar integration
- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Voice input
- [ ] Recurring todos
- [ ] Task dependencies

---

## Reusability

This project reuses ~70% of code from previous hackathons:

| From | Reused |
|------|--------|
| H0 | Vault structure, HITL workflow |
| H1 | Constitutional validator patterns, FastAPI setup |
| H1 | Next.js configuration, TypeScript setup |

---

## Credits

Developed as part of the Hackathon Completion Engine project.

- **Developer**: Asadullah Shafique
- **Tier**: Silver
- **Time**: ~7 hours across 4 sessions

---

## License

MIT License - See LICENSE file for details.

---

*Built with Constitutional AI for ethical task management*
