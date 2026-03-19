# H2: AI-Powered Todo App
**Zero-Backend-LLM Architecture with Constitutional Compliance**

[![Status](https://img.shields.io/badge/status-silver%20tier-silver)]()
[![Tests](https://img.shields.io/badge/tests-15%2B%20passing-brightgreen)]()
[![TypeScript](https://img.shields.io/badge/typescript-5.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

> AI-powered todo application that uses constitutional rules to prevent harmful task creation while enabling intelligent natural language parsing.

---

## 🎯 Overview

H2 demonstrates **Zero-Backend-LLM architecture** where all AI logic runs client-side in the frontend, with the backend serving only as a data persistence layer. This architectural pattern enables rapid AI iteration without backend redeployment.

**Key Innovation:** Constitutional AI enforcement prevents users from creating todos that violate academic integrity, legal boundaries, or ethical standards.

---

## ✨ Features

### Constitutional AI Enforcement
- ✅ **7 BLOCK patterns** - Prevents academic dishonesty, illegal activities, harmful content
- ✅ **5 FLAG patterns** - Identifies suspicious tasks for human review
- ✅ **Triple-layer validation** - Frontend + Backend + HITL queue
- ✅ **Transparent decisions** - Shows why tasks are blocked/flagged

### AI-Powered Task Management
- 🤖 **Natural language parsing** - "Buy milk tomorrow" → structured todo
- 🏷️ **Smart categorization** - AI infers category (work/personal/study/health/other)
- ⚡ **Priority inference** - Detects urgency from context
- 📅 **Deadline extraction** - Converts "tomorrow", "Friday 2pm" to dates
- 💯 **Confidence scoring** - Shows parsing reliability

### Full-Stack CRUD
- ➕ Create todos with AI assistance
- 📝 Update title, description, category, priority, deadline
- ✅ Mark complete with status tracking
- 🗑️ Delete with confirmation
- 🔍 Search across title and description
- 🎚️ Filter by category, status, priority, deadline

### Statistics Dashboard
- 📊 Completion rate with progress bar
- 📈 Breakdown by status (pending/in_progress/completed/flagged)
- 🎯 Category distribution
- ⚠️ Priority distribution
- 🔥 Today's focus (overdue + high priority)

### Professional UI
- 🎨 Tailwind CSS styling
- 📱 Responsive design (mobile + desktop)
- 🌙 Clean, modern interface
- 🎭 Grid/List view toggle
- 🔔 Toast notifications
- ⚡ Optimistic updates

---

## 🏗️ Architecture

### Zero-Backend-LLM Pattern
```
┌─────────────────────────────────────┐
│   Frontend (Next.js + TypeScript)   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   AI Logic (Client-Side)    │   │
│  │  • OpenAI API integration   │   │
│  │  • Natural language parsing │   │
│  │  • Constitutional filtering │   │
│  │  • Priority inference       │   │
│  │  • Category detection       │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   UI Components             │   │
│  │  • Todo list                │   │
│  │  • Create form              │   │
│  │  • Filters                  │   │
│  │  • Stats dashboard          │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ REST API (CRUD only)
               ▼
┌─────────────────────────────────────┐
│   Backend (FastAPI + Python)        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   Data Layer (No AI)        │   │
│  │  • CRUD operations          │   │
│  │  • SQLAlchemy ORM           │   │
│  │  • SQLite database          │   │
│  │  • Constitutional backup    │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Vault (Obsidian)                  │
│  • Constitutional rules             │
│  • HITL approval queue              │
│  • Activity logs                    │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn
- OpenAI API key (optional - works with mock responses)

### Installation
```bash
# Clone repository
cd hackathons/h2-todo-spec-driven

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your DATABASE_URL

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local and add NEXT_PUBLIC_OPENAI_API_KEY (optional)
```

### Running
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Open http://localhost:3000
```

---

## 📋 Constitutional Rules

### ❌ Prohibited (Blocked)

**Academic Dishonesty:**
- "Do my homework assignment"
- "Write my essay for me"
- "Complete my coding project"
- "Take my exam"

**Illegal Activities:**
- "Hack into [system]"
- "Create fake documents"
- "Bypass security"

**Harmful Content:**
- "Harass [person]"
- "Spread misinformation"

### ✅ Allowed

**Legitimate Work:**
- "Study chapter 5 for exam"
- "Practice coding exercises"
- "Research topic for paper"
- "Complete work project"

**Personal Growth:**
- "Exercise for 30 minutes"
- "Read [book]"
- "Learn [skill]"

### 🚩 Flagged (HITL Review)

**Time Pressure + Academic:**
- "Urgent: finish assignment in 1 hour"
- "Exam tomorrow, need to complete this"

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest ../tests/ -v
```

**Coverage:**
- Constitutional validation (6 tests)
- CRUD operations (8 tests)
- Database models (3 tests)
- **Total:** 15+ tests

### Frontend Tests
```bash
cd frontend
npm test
```

**Coverage:**
- AI parsing (5 tests)
- Constitutional filtering (4 tests)

---

## 📊 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database (dev)
- **Pydantic** - Data validation
- **pytest** - Testing framework

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Zustand** - State management
- **OpenAI API** - GPT-3.5-turbo for parsing
- **axios** - HTTP client
- **Lucide React** - Icon library

### Infrastructure
- **Vault (Obsidian)** - Constitutional rules + HITL queue
- **Git** - Version control
- **GitHub** - Repository hosting

---

## 🎨 UI Components

### CreateTodoForm
- Natural language textarea
- "Parse with AI ✨" button
- Parsed result preview
- Manual override fields
- Constitutional guard alerts

### TodoList
- Grid/List view toggle
- Sortable and groupable
- Status badges
- Priority indicators
- Category tags

### TodoFilters
- Multi-select dropdowns
- Debounced search
- Active filter badges
- Clear all button

### TodoStats
- Completion rate progress bar
- Status breakdown cards
- Category distribution
- Priority distribution

### EditTodoModal
- Slide-in panel
- Pre-filled form
- Constitutional re-validation
- Delete confirmation

---

## 🔮 Future Enhancements (Gold Tier)

- [ ] Recurring todos (daily, weekly, monthly)
- [ ] Todo templates (pre-configured tasks)
- [ ] Team collaboration (shared todos)
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Advanced analytics (productivity insights)
- [ ] Mobile app (React Native)
- [ ] Offline mode (PWA)
- [ ] AI suggestions ("Based on your todos...")
- [ ] Voice input (speech-to-text)
- [ ] Email notifications

---

## 🔧 Configuration

### Backend (.env)
```bash
DATABASE_URL=sqlite:///./todos.db
VAULT_PATH=../vault
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_API_KEY=sk-... # Optional
```

---

## 📖 API Documentation

### Endpoints

**POST /api/todos**
```json
Request: {
  "title": "Study for exam",
  "description": "Review chapters 1-5",
  "category": "study",
  "priority": "high",
  "deadline": "2026-01-30T00:00:00Z"
}

Response: {
  "id": "uuid",
  "constitutional_check": {
    "passed": true,
    "decision": "allow"
  },
  ...
}
```

**GET /api/todos**
Query params: `category`, `status`, `priority`, `search`

**PUT /api/todos/{id}**  
**DELETE /api/todos/{id}**  
**GET /api/stats**

---

## 🙏 Credits & Reusability

**Built on Foundation From:**
- **H0 (Personal AI CTO):** Vault structure, HITL workflow, logging patterns
- **H1 (Course Companion):** Constitutional filter (90%), FastAPI backend (80%), Next.js setup (70%)

**Reusability:** ~70% code reused from H0+H1

**Methodology:** Spec-driven development with systematic 4-session execution

---

## 👨‍💻 Developer

**Asadullah Shafique**  
GitHub: [@asadullah48](https://github.com/asadullah48)  
Project: Panaversity Hackathon Series (H0-H4)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎯 Hackathon Achievement

**Tier:** Silver ✅  
**Time:** 6-7 hours  
**Tests:** 15+ passing  
**Status:** Production Ready  

Part of systematic hackathon completion framework demonstrating:
- Spec-driven development
- Constitutional AI
- Zero-Backend-LLM architecture
- Component reusability

---

**Built with ❤️ for responsible AI development**  
**January 2026 - Panaversity Hackathon Series**
