# SPEC-H2-CORE: Todo Spec-Driven Development
**Zero-Backend-LLM Task Management with Constitutional Compliance**

**Version:** 1.0
**Date:** 2026-01-25
**Target Tier:** Silver (Gold stretch)
**Estimated Time:** 6-7 hours
**Reuses from H0+H1:** 70%

---

## 1. OVERVIEW

### Purpose
A production-grade todo application demonstrating spec-driven development methodology with zero-backend-LLM architecture. All AI logic runs in the frontend, with FastAPI serving only as data persistence layer.

### Core Innovation
**Constitutional Compliance Framework** - Prevents AI from creating todos that violate:
- Academic integrity (no "do homework for me")
- Legal boundaries (no illegal activities)
- Ethical standards (no harmful tasks)
- Professional conduct (no unethical business practices)

### Key Differentiator
Unlike typical todo apps, this enforces **constitutional rules** on task creation, demonstrating responsible AI development for business applications.

---

## 2. ARCHITECTURE

### Zero-Backend-LLM Principle
```
Frontend (Next.js)
├── AI Logic (100% client-side)
│   ├── Task parsing with ChatGPT API
│   ├── Priority inference
│   ├── Category detection
│   ├── Deadline extraction
│   └── Constitutional filtering
│
Backend (FastAPI)
├── Data persistence only (NO AI logic)
│   ├── CRUD operations
│   ├── Database (SQLite/PostgreSQL)
│   └── Simple REST API
│
Vault (From H0)
└── Constitutional rules storage
```

---

## 3. CONSTITUTIONAL RULES FOR TODOS

### Prohibited Todo Types ❌

**Academic Dishonesty:**
- "Do my homework assignment"
- "Write my essay"
- "Complete my coding project"
- "Take my exam"

**Illegal Activities:**
- "Hack into [system]"
- "Create fake documents"
- "Bypass security measures"

**Harmful Actions:**
- "Harass [person]"
- "Spread misinformation"
- "Create harmful content"

### Allowed Todo Types ✅

**Legitimate Work:**
- "Study chapter 5 for exam"
- "Practice coding exercises"
- "Research topic for paper"
- "Prepare presentation outline"

**Personal Growth:**
- "Learn new skill"
- "Exercise for 30 minutes"
- "Read [book]"

---

## 4. REUSABLE COMPONENTS FROM H0+H1

| Component | Source | H2 Adaptation | Reuse % |
|-----------|--------|---------------|---------|
| Constitutional Filter | H1 | Todo content validation | 90% |
| Vault Structure | H0 | Constitutional rules storage | 100% |
| HITL Workflow | H0 | Flagged todos approval | 100% |
| FastAPI Backend | H1 | CRUD operations | 80% |
| Next.js Frontend | H1 | Todo UI | 70% |
| Testing Framework | H1 | Todo tests | 85% |
| Logger Service | H1 | Activity logging | 95% |

**Overall Reuse:** ~70% from H0+H1

---

## 5. FEATURES BY TIER

### Bronze Tier (Minimum)
- Create/Read/Update/Delete todos
- Constitutional filtering (block prohibited todos)
- Basic categorization (work, personal, study)
- Simple priority (high, medium, low)
- SQLite persistence
- Activity logging

### Silver Tier (Target)
- AI-powered task parsing ("Buy milk tomorrow" → deadline, category, priority)
- Smart categorization (AI infers category)
- Priority inference (AI determines urgency)
- Deadline extraction (natural language → date)
- HITL approval for flagged todos
- Search and filter
- Statistics dashboard
- Zero-Backend-LLM architecture validated

### Gold Tier (Stretch)
- Recurring todos
- Todo templates
- Team collaboration
- AI suggestions
- Calendar integration
- Mobile-responsive PWA
- Advanced analytics

---

## 6. TECH STACK

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- OpenAI API (client-side only)
- Zustand (state management)

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy (ORM)
- SQLite (development) / PostgreSQL (production)
- Pydantic (validation)

**Testing:**
- pytest (backend)
- Vitest (frontend)
- Playwright (E2E optional)

---

## 7. DATA MODEL

### Todo Schema
```typescript
interface Todo {
  id: string;
  title: string;
  description?: string;
  category: 'work' | 'personal' | 'study' | 'health' | 'other';
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed' | 'flagged';
  deadline?: Date;
  created_at: Date;
  updated_at: Date;
  constitutional_check: {
    passed: boolean;
    decision: 'allow' | 'block' | 'flag';
    reason?: string;
  };
  ai_metadata?: {
    inferred_category: string;
    inferred_priority: string;
    extracted_deadline: string;
    confidence: number;
  };
}
```

### API Endpoints
```
POST   /api/todos          - Create todo (with constitutional check)
GET    /api/todos          - List todos (with filters)
GET    /api/todos/:id      - Get single todo
PUT    /api/todos/:id      - Update todo
DELETE /api/todos/:id      - Delete todo
GET    /api/stats          - Get statistics
POST   /api/todos/parse    - Parse natural language (frontend only)
```

---

## 8. FOUR-SESSION IMPLEMENTATION

### Session 1: Foundation & CRUD (1.5 hours)
**Focus:** Database models, CRUD operations, constitutional validation

**Deliverables:**
- SQLAlchemy models (Todo, enums)
- FastAPI CRUD endpoints
- Constitutional validator (adapted from H1)
- Database setup (SQLite)
- Basic tests (CRUD + constitutional)

**Files Created:** ~12 files

---

### Session 2: AI Integration (2 hours)
**Focus:** Zero-Backend-LLM implementation, AI parsing

**Deliverables:**
- Frontend OpenAI integration
- Natural language parsing
- Smart categorization
- Priority inference
- Deadline extraction
- Constitutional filtering (frontend)
- Mock responses (no API key fallback)

**Files Created:** ~8 files

---

### Session 3: Frontend UI (2 hours)
**Focus:** Todo interface, user experience

**Deliverables:**
- Todo list component
- Create todo form (with AI parsing)
- Edit/Delete functionality
- Filter & search UI
- Statistics dashboard
- Constitutional guard visualization
- Responsive design

**Files Created:** ~10 files

---

### Session 4: Testing & Validation (1.5 hours)
**Focus:** Quality assurance, documentation

**Deliverables:**
- Comprehensive test suite
- E2E validation
- Constitutional enforcement testing
- README.md (300+ lines)
- COMPLETION_REPORT.md
- Silver tier validation

**Files Created:** ~5 files

---

## 9. SUCCESS CRITERIA

### Must Pass (Bronze)
- ✅ All CRUD operations working
- ✅ Constitutional filter blocks prohibited todos
- ✅ Basic UI functional
- ✅ SQLite persistence working
- ✅ All tests passing (20+ tests)

### Should Pass (Silver)
- ✅ AI parsing working correctly
- ✅ Zero-Backend-LLM architecture proven
- ✅ HITL approval queue functional
- ✅ Statistics dashboard complete
- ✅ Search/filter operational
- ✅ Professional UI with Tailwind

### Nice to Have (Gold)
- ✅ Recurring todos
- ✅ Templates
- ✅ Team features
- ✅ Calendar integration

---

## 10. VALIDATION TESTS

**Constitutional Enforcement:**
```
❌ Block: "Do my homework assignment"
❌ Block: "Hack into database"
✅ Allow: "Study for exam tomorrow"
✅ Allow: "Complete work project"
🚩 Flag: "Urgent: finish assignment in 1 hour"
```

**AI Parsing:**
```
Input:  "Buy milk tomorrow"
Output: deadline=tomorrow, category=personal, priority=low

Input:  "Urgent: client meeting prep"
Output: priority=high, category=work

Input:  "Study chapter 5 for Friday exam"
Output: deadline=Friday, category=study, priority=medium
```

**CRUD Operations:**
```
✅ Create → appears in list
✅ Update → changes reflected
✅ Delete → removed
✅ Filter by category → correct subset
✅ Search → relevant results
```

---

## 11. RISK MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI parsing errors | Medium | Confidence scores + manual override |
| Constitutional bypass | High | Triple validation (frontend + backend + HITL) |
| Zero-Backend complexity | Medium | Clear docs + separation of concerns |
| API costs | Low | Rate limiting + caching + mock fallback |
| Performance | Low | SQLite adequate for demo |

---

## 12. DEPENDENCIES

**Required:**
- OpenAI API key (or use mock responses)
- Python 3.11+
- Node.js 18+
- Git

**Optional:**
- PostgreSQL (production)
- Docker (deployment)

---

## 13. ESTIMATED TIMELINE

**Session 1:** 1.5 hours (Foundation)
**Session 2:** 2 hours (AI Integration)
**Session 3:** 2 hours (Frontend)
**Session 4:** 1.5 hours (Validation)
**Total:** 6-7 hours

**With breaks:** Can complete in 1 day

---

## 14. NEXT STEPS AFTER H2

**H3: Advanced Todo Features**
- Build on H2 foundation
- Add advanced features from Gold tier
- Team collaboration
- Advanced analytics

**H4: Cloud Deployment**
- Deploy H2+H3 to production
- Kubernetes configuration
- CI/CD pipeline
- Monitoring & scaling

---

**Specification Status:** ✅ Complete
**Ready for:** Session 1 execution
**Author:** Asadullah Shafique
**Date:** 2026-01-25
