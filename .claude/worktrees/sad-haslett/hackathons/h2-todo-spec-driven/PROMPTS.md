# H2 IMPLEMENTATION PROMPTS
**Ready-to-paste prompts for Claude Code**

---

## SESSION 1: Foundation & CRUD (1.5 hours)
```
IMPLEMENTATION: H2 Todo Spec-Driven - Session 1 (Foundation)

CONTEXT:
Building Zero-Backend-LLM todo app with constitutional compliance. Reusing 70% from H0+H1 (vault structure, constitutional filter, FastAPI patterns, Next.js setup).

PREREQUISITES:
✅ H0 complete (vault structure, HITL workflow)
✅ H1 complete (constitutional filter, FastAPI backend, Next.js frontend)
✅ H2 spec reviewed: /mnt/d/Personal-AI-Employee/specs/SPEC-H2-CORE.md

PROJECT LOCATION: /mnt/d/Personal-AI-Employee/hackathons/h2-todo-spec-driven/

---

TASK 1.1: Create Directory Structure

Create this structure:
h2-todo-spec-driven/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── todos.py
│   │   └── stats.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── constitutional_validator.py
│   ├── database.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── components/
│   │   └── (placeholders for Session 3)
│   ├── lib/
│   │   ├── constitutionalTodoFilter.ts
│   │   └── api.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
│
├── vault/ (copy structure from H0)
│   ├── Constitutional_Rules/
│   │   └── todo-rules.md
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   └── Logs/
│
├── tests/
│   ├── __init__.py
│   ├── test_constitutional_todos.py
│   ├── test_crud_operations.py
│   └── test_models.py
│
└── README.md (placeholder)

---

TASK 1.2: Constitutional Validator Service

Create: backend/services/constitutional_validator.py

Adapt from H1's constitutional filter. Requirements:
- Pattern matching for prohibited todo content
- Allow/Block/Flag decisions
- HITL approval creation for flagged items
- Logging all decisions

Prohibited patterns (from SPEC section 3):
- Academic dishonesty: homework, essay, exam completion
- Illegal activities: hacking, fake documents
- Harmful actions: harassment, misinformation

Keep: same validation logic, HITL approval creation
Update: error messages for todo context

---

TASK 1.3: Create Todo Model

Create: backend/models/todo.py

Requirements:
- SQLAlchemy declarative base
- Enums: TodoCategory, TodoPriority, TodoStatus
- Todo model with fields:
  - id (UUID primary key)
  - title (required)
  - description (optional)
  - category (enum, default OTHER)
  - priority (enum, default MEDIUM)
  - status (enum, default PENDING)
  - deadline (DateTime, optional)
  - created_at, updated_at (auto timestamps)
  - constitutional_check (JSON: {passed, decision, reason})
  - ai_metadata (JSON, optional: {inferred_category, priority, deadline, confidence})

---

TASK 1.4: Database Setup

Create: backend/database.py

Requirements:
- SQLite connection string: sqlite:///./todos.db
- SQLAlchemy engine with connection pooling
- Session factory
- get_db() dependency for FastAPI
- init_db() to create all tables

---

TASK 1.5: CRUD Router

Create: backend/routers/todos.py

Endpoints:

POST /api/todos
- Input: {title, description?, category?, priority?, deadline?}
- Process: Constitutional check → Create todo → Log
- Output: Created todo with constitutional_check field

GET /api/todos
- Query params: category?, status?, priority?, search?
- Filter todos based on params
- Output: List of todos

GET /api/todos/{id}
- Output: Single todo or 404

PUT /api/todos/{id}
- Input: {title?, description?, category?, priority?, status?, deadline?}
- Process: Constitutional check (if title/description changed)
- Output: Updated todo

DELETE /api/todos/{id}
- Output: {deleted: true, id}

All endpoints use constitutional_validator.check_query() on title/description.

---

TASK 1.6: Stats Router

Create: backend/routers/stats.py

GET /api/stats

Calculate and return:
```json
{
  "total": 50,
  "by_status": {
    "pending": 20,
    "in_progress": 5,
    "completed": 25,
    "flagged": 0
  },
  "by_category": {
    "work": 30,
    "personal": 15,
    "study": 5,
    "health": 0,
    "other": 0
  },
  "by_priority": {
    "high": 10,
    "medium": 25,
    "low": 15
  },
  "completion_rate": 0.5
}
```

---

TASK 1.7: Main FastAPI App

Create: backend/main.py

Include:
- FastAPI app initialization
- CORS middleware (allow localhost:3000)
- Database initialization on startup
- Include routers: todos, stats
- Health check endpoint
- Root endpoint with API info

---

TASK 1.8: Requirements

Create: backend/requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.2
```

Create: backend/.env.example
```
DATABASE_URL=sqlite:///./todos.db
VAULT_PATH=../vault
```

---

TASK 1.9: Constitutional Rules Document

Create: vault/Constitutional_Rules/todo-rules.md

Document all prohibited patterns, allowed patterns, and enforcement mechanisms (copied from SPEC-H2-CORE.md section 3).

---

TASK 1.10: Backend Tests

Create: tests/test_constitutional_todos.py

Tests:
- test_prohibited_homework_blocked()
- test_prohibited_hacking_blocked()
- test_prohibited_cheating_blocked()
- test_allowed_study_todo()
- test_allowed_work_todo()
- test_flagged_urgent_todo()

Create: tests/test_crud_operations.py

Tests:
- test_create_todo_success()
- test_create_todo_constitutional_block()
- test_list_todos_empty()
- test_list_todos_with_data()
- test_filter_by_category()
- test_filter_by_status()
- test_update_todo()
- test_delete_todo()
- test_get_todo_not_found()

Create: tests/test_models.py

Tests:
- test_todo_model_creation()
- test_todo_enums()
- test_todo_defaults()

---

VALIDATION:

```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h2-todo-spec-driven

# Install dependencies
cd backend
pip3 install -r requirements.txt

# Run tests
cd ..
python3 -m pytest tests/ -v

# Start server
cd backend
uvicorn main:app --reload &
sleep 3

# Test endpoints
echo "=== Testing CRUD ==="

# Create allowed todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Study for exam tomorrow", "category": "study", "priority": "high"}'

# Create blocked todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Do my homework assignment", "category": "study"}'

# List todos
curl http://localhost:8000/api/todos

# Get stats
curl http://localhost:8000/api/stats

# Kill server
pkill -f uvicorn
```

---

DELIVERABLES:
1. Complete backend structure (15+ files)
2. Constitutional validator adapted from H1
3. Todo model with SQLAlchemy
4. CRUD endpoints working
5. Stats endpoint functional
6. All tests passing (15+ tests)
7. Constitutional enforcement verified

Show me:
- Test results (all passing)
- Sample API responses (blocked + allowed)
- Stats endpoint output
- File count and structure

Execute all tasks. After validation, ready for Session 2.
```

---

## SESSION 2: AI Integration (2 hours)
```
IMPLEMENTATION: H2 Session 2 - AI Integration (Zero-Backend-LLM)

PREREQUISITES: ✅ Session 1 complete (backend operational)

OBJECTIVE: Implement frontend AI parsing with constitutional filtering

---

TASK 2.1: OpenAI Client (Frontend)

Create: frontend/lib/openaiClient.ts

Client-side OpenAI integration:
- Configuration from env variables
- chat.completions.create wrapper
- Error handling
- Rate limiting (10 requests/min)
- Mock responses when no API key

---

TASK 2.2: AI Todo Parser

Create: frontend/lib/aiTodoParser.ts

Function: parseTodoWithAI(naturalLanguageInput: string)

Returns:
```typescript
{
  title: string;
  description?: string;
  category: TodoCategory;
  priority: TodoPriority;
  deadline?: Date;
  confidence: number;
  ai_metadata: {...}
}
```

System prompt:
```
You are a todo parser. Extract structured data from natural language.

Input: "Buy milk tomorrow"
Output: {
  "title": "Buy milk",
  "category": "personal",
  "priority": "low",
  "deadline": "2026-01-26",
  "confidence": 0.9
}

Categories: work, personal, study, health, other
Priorities: high, medium, low
```

---

TASK 2.3: Constitutional Todo Filter (Frontend)

Create: frontend/lib/constitutionalTodoFilter.ts

Same patterns as backend validator.

Function: checkTodoContent(content: string)
Returns: {allowed: boolean, decision: string, reason?: string}

---

TASK 2.4: API Client

Create: frontend/lib/api.ts

Functions:
- createTodo(todo: Partial<Todo>)
- getTodos(filters?: {category, status, priority})
- updateTodo(id: string, updates: Partial<Todo>)
- deleteTodo(id: string)
- getStats()

Use axios with error handling.

---

TASK 2.5: Frontend Tests

Create: tests/test_ai_parsing.test.ts (Vitest)

Tests:
- test_parse_simple_todo()
- test_parse_with_deadline()
- test_parse_with_priority()
- test_constitutional_check()
- test_mock_response_when_no_api_key()

---

VALIDATION:

```bash
# Test AI parsing locally
cd frontend
npm install
npm test

# Manual test
node -e "
  const { parseTodoWithAI } = require('./lib/aiTodoParser.ts');
  parseTodoWithAI('Buy milk tomorrow').then(console.log);
"
```

Show: AI parsing working, constitutional filter functional.

Ready for Session 3.
```

---

## SESSION 3: Frontend UI (2 hours)
```
IMPLEMENTATION: H2 Session 3 - Frontend UI

PREREQUISITES: ✅ Session 2 complete (AI parsing ready)

---

TASK 3.1: Initialize Next.js (if not done)

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install axios date-fns lucide-react zustand
```

---

TASK 3.2: Todo List Component

Create: frontend/components/TodoList.tsx

Features:
- Display todos with category badges
- Priority indicators (color-coded)
- Status toggle (pending → in_progress → completed)
- Edit button
- Delete button
- Constitutional decision indicator (if blocked/flagged)

---

TASK 3.3: Create Todo Form

Create: frontend/components/CreateTodoForm.tsx

Features:
- Natural language input
- "Parse with AI" button
- Shows parsed result (title, category, priority, deadline)
- Manual override fields
- Constitutional guard (shows if blocked)
- Submit button

---

TASK 3.4: Filter & Search

Create: frontend/components/TodoFilters.tsx

Filters:
- Category dropdown
- Status dropdown
- Priority dropdown
- Search input
- Clear filters button

---

TASK 3.5: Stats Dashboard

Create: frontend/components/TodoStats.tsx

Display:
- Total todos
- Completion rate
- By category (pie chart or bars)
- By priority
- By status

Use chart library or simple CSS bars.

---

TASK 3.6: Main Page

Update: frontend/app/page.tsx

Layout:
- Header with "Todo App" title
- CreateTodoForm
- TodoFilters
- TodoList
- TodoStats (sidebar)

Responsive design.

---

VALIDATION:

Start both servers and test E2E:

```bash
# Backend
cd backend
uvicorn main:app --reload &

# Frontend
cd ../frontend
npm run dev &

# Open http://localhost:3000
# Test:
# 1. Create todo with AI parsing
# 2. Filter by category
# 3. Update todo status
# 4. Delete todo
# 5. View stats
```

Show: Full UI working, AI parsing integrated.

Ready for Session 4.
```

---

## SESSION 4: Testing & Validation (1.5 hours)
```
IMPLEMENTATION: H2 Session 4 - Final Validation

PREREQUISITES: ✅ Sessions 1-3 complete

---

TASK 4.1: Comprehensive Testing

Run all tests:

```bash
# Backend
python3 -m pytest tests/ -v

# Frontend
cd frontend
npm test
```

Expected: 25+ tests passing.

---

TASK 4.2: E2E Validation

Manual checklist:
- [ ] Create todo with AI parsing
- [ ] Constitutional block works
- [ ] CRUD operations functional
- [ ] Filters work correctly
- [ ] Stats update in real-time
- [ ] UI responsive

---

TASK 4.3: Documentation

Create: README.md (300+ lines)
Create: COMPLETION_REPORT.md

Include tier assessment (Bronze/Silver/Gold).

---

TASK 4.4: Silver Tier Validation

Verify all Silver requirements met.

---

DELIVERABLES:
- All tests passing
- README complete
- Tier certification
- Production ready

Show final report.
```

---

**END OF PROMPTS**
