# SPEC-H1-CORE: Course Companion FTE
**AI-Powered Learning Assistant with Constitutional Rules**

**Version:** 1.0  
**Date:** 2026-01-23  
**Target Tier:** Silver (Bronze minimum)  
**Estimated Time:** 7 hours  
**Reuses from H0:** 60%

---

## 1. OVERVIEW

### Purpose
An AI-powered course companion that helps students learn programming and technical concepts through Socratic guidance while enforcing strict academic integrity rules.

### Core Principle
**Guide, don't solve.** Help students think, never do their thinking for them.

### Key Features
- ChatGPT-powered conversational AI
- Constitutional rules enforcement (unbreakable)
- Zero-Backend-LLM architecture
- FastAPI lightweight backend
- HITL oversight for sensitive queries
- Obsidian vault integration (reused from H0)
- Real-time conversation logging

---

## 2. CONSTITUTIONAL RULES (CRITICAL)

### Absolute Prohibitions ❌
**The system MUST NEVER:**
1. Provide complete homework solutions
2. Write full code implementations for assignments
3. Take exams or quizzes for students
4. Give direct answers to graded questions
5. Bypass academic integrity policies

### Required Behaviors ✅
**The system MUST ALWAYS:**
1. Use Socratic questioning (ask questions, not answers)
2. Explain concepts thoroughly
3. Provide hints and guidance
4. Encourage independent problem-solving
5. Log all interactions for review
6. Flag suspicious queries for HITL approval

### Enforcement Layers
1. **System Prompt** - ChatGPT system message with rules
2. **Middleware Filter** - Backend code validation
3. **Frontend Guard** - UI-level enforcement
4. **HITL Queue** - Human review for edge cases

---

## 3. ARCHITECTURE

### Tech Stack
```
Frontend: Next.js 14 + React 18 + TypeScript
Backend: FastAPI + Python 3.11+
AI: OpenAI ChatGPT API (gpt-3.5-turbo)
Database: SQLite (local-first)
Vault: Obsidian/Markdown (reused from H0)
Testing: pytest + React Testing Library
```

### System Components
```
Course Companion (H1)
│
├── Frontend (Next.js)
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── CourseMaterialViewer.tsx
│   │   ├── ProgressDashboard.tsx
│   │   └── ConstitutionalGuard.tsx
│   ├── lib/
│   │   ├── chatLogic.ts (Zero-Backend)
│   │   └── constitutionalRules.ts
│   └── app/
│       └── page.tsx
│
├── Backend (FastAPI)
│   ├── main.py
│   ├── routers/
│   │   ├── chat.py
│   │   └── materials.py
│   ├── middleware/
│   │   └── constitutional_filter.py
│   ├── services/
│   │   ├── chatgpt_service.py
│   │   └── logger_service.py (from H0)
│   └── models/
│       └── conversation.py
│
├── Vault (From H0)
│   ├── Course_Materials/
│   ├── Student_Progress/
│   ├── Conversation_Logs/
│   ├── Pending_Approval/
│   └── Dashboard.md
│
└── Skills
    ├── constitutional-rules.md (new)
    ├── socratic-tutoring.md (new)
    └── hitl-approval-manager.md (from H0)
```

---

## 4. REUSABLE COMPONENTS FROM H0

### Direct Reuse (60%)
| Component | H0 Location | H1 Adaptation |
|-----------|-------------|---------------|
| Vault Structure | `vault/*` | Add Course_Materials/, Student_Progress/ |
| HITL Workflow | `skills/hitl-approval-manager.md` | Use for sensitive queries |
| Activity Logger | `watchers/file_watcher.py::_log_activity()` | Adapt for conversation logging |
| Dashboard Template | `vault/Dashboard.md` | Modify for student progress |
| State Persistence | `.file_watcher_state.json` pattern | Use for conversation history |

### Modified Reuse (30%)
| Component | Modification |
|-----------|--------------|
| FileWatcher → ConversationWatcher | Monitor chats instead of files |
| Action Items → Learning Tasks | Track student progress |
| Approval Queue | Flag suspicious queries |

### New Components (10%)
- ChatGPT API integration
- Constitutional middleware
- React chat interface
- Course material viewer

---

## 5. DATA FLOW

### User Interaction Flow
```
1. Student asks question
   ↓
2. Frontend: Constitutional guard checks query
   ↓
3. Backend: Middleware validates intent
   ↓
4. ChatGPT API: Generates Socratic response
   ↓
5. Backend: Logs conversation
   ↓
6. Frontend: Displays response
   ↓
7. Vault: Stores conversation + progress
```

### Suspicious Query Flow
```
1. Constitutional guard detects potential violation
   ↓
2. Query sent to Pending_Approval/
   ↓
3. Human reviews intent
   ↓
4. If approved → Process query
   If rejected → Explain to student why
```

---

## 6. CONSTITUTIONAL RULES ENFORCEMENT

### System Prompt Template
```
You are a Course Companion AI tutor. Your role is to guide students to discover answers themselves, not provide direct solutions.

CONSTITUTIONAL RULES (UNBREAKABLE):
1. Never provide complete homework solutions
2. Never write full code for assignments
3. Never give direct answers to graded work
4. Always use Socratic questioning
5. Always explain concepts, never just answers

When a student asks for help:
- Ask what they've tried already
- Guide them with hints
- Explain the concept behind the problem
- Encourage them to attempt the solution
- Celebrate their thinking process

If a query seems like cheating:
- Politely decline
- Explain academic integrity
- Offer to teach the underlying concept instead
```

### Middleware Validation Rules
```python
PROHIBITED_PATTERNS = [
    r"solve this (homework|assignment|test|quiz)",
    r"write (the|this) code for me",
    r"give me the answer",
    r"do my (homework|assignment)",
    r"complete this for me"
]

SUSPICIOUS_PATTERNS = [
    r"(exam|test|quiz) tomorrow",
    r"due in \d+ (hour|minute)",
    r"need answer (now|asap|urgent)"
]
```

---

## 7. SILVER TIER FEATURES

### Bronze Requirements (Minimum)
- [x] ChatGPT integration working
- [x] Constitutional rules enforced
- [x] Basic chat interface
- [x] Conversation logging
- [x] HITL approval queue

### Silver Requirements (Target)
- [ ] Multi-turn conversations with context
- [ ] Course material viewer integrated
- [ ] Progress tracking dashboard
- [ ] Student learning analytics
- [ ] Response quality rating system

### Gold Requirements (Stretch)
- [ ] Multi-student support
- [ ] Advanced analytics (time spent, concepts mastered)
- [ ] Adaptive difficulty adjustment
- [ ] Integration with course LMS
- [ ] Mobile-responsive design

---

## 8. API SPECIFICATIONS

### Backend Endpoints

**POST /api/chat**
```json
Request:
{
  "message": "How do I solve this sorting problem?",
  "conversation_id": "conv_123",
  "student_id": "student_456"
}

Response:
{
  "response": "Great question! Let's think about what sorting means...",
  "conversation_id": "conv_123",
  "needs_approval": false,
  "logged": true
}
```

**GET /api/progress/{student_id}**
```json
Response:
{
  "student_id": "student_456",
  "conversations": 23,
  "concepts_learned": ["sorting", "recursion", "arrays"],
  "time_spent_minutes": 145,
  "last_active": "2026-01-23T10:30:00Z"
}
```

**GET /api/materials**
```json
Response:
{
  "materials": [
    {
      "id": "mat_1",
      "title": "Intro to Sorting",
      "path": "vault/Course_Materials/sorting.md",
      "category": "algorithms"
    }
  ]
}
```

---

## 9. FILE STRUCTURE
```
h1-course-companion/
├── frontend/                    # Next.js app
│   ├── app/
│   │   ├── page.tsx            # Main chat page
│   │   ├── progress/page.tsx   # Progress dashboard
│   │   └── materials/page.tsx  # Course materials
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── ConstitutionalGuard.tsx
│   │   └── ProgressChart.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── constitutionalRules.ts
│   │   └── utils.ts
│   └── package.json
│
├── backend/                     # FastAPI app
│   ├── main.py
│   ├── routers/
│   │   ├── chat.py
│   │   ├── progress.py
│   │   └── materials.py
│   ├── middleware/
│   │   └── constitutional_filter.py
│   ├── services/
│   │   ├── chatgpt_service.py
│   │   ├── logger_service.py
│   │   └── vault_service.py
│   ├── models/
│   │   └── conversation.py
│   ├── requirements.txt
│   └── .env.example
│
├── vault/                       # From H0
│   ├── Course_Materials/
│   ├── Student_Progress/
│   ├── Conversation_Logs/
│   ├── Pending_Approval/
│   └── Dashboard.md
│
├── skills/
│   ├── constitutional-rules.md
│   ├── socratic-tutoring.md
│   └── hitl-approval-manager.md
│
├── tests/
│   ├── test_constitutional_rules.py
│   ├── test_chat_endpoint.py
│   └── test_frontend_guard.py
│
└── README.md
```

---

## 10. TESTING STRATEGY

### Unit Tests
```python
# Test constitutional rules
def test_homework_request_blocked():
    query = "Solve this homework for me"
    assert is_prohibited(query) == True

def test_concept_question_allowed():
    query = "Can you explain how sorting works?"
    assert is_prohibited(query) == False

# Test Socratic response
def test_socratic_questioning():
    response = generate_response("What's the answer to 2+2?")
    assert "what do you think" in response.lower()
    assert "4" not in response
```

### Integration Tests
- E2E conversation flow
- Constitutional enforcement across layers
- HITL approval workflow
- Vault logging

### Adversarial Tests
- Attempt to bypass constitutional rules
- Test edge cases (urgent deadlines, exam questions)
- Verify all prohibitions enforced

---

## 11. FOUR-SESSION IMPLEMENTATION

### Session 1: Foundation (1.5 hours)
**Deliverables:**
- Directory structure created
- FastAPI skeleton with constitutional middleware
- Constitutional rules skill document
- Vault folders initialized
- .env configured with API key

**Key Files:**
- `backend/main.py`
- `backend/middleware/constitutional_filter.py`
- `skills/constitutional-rules.md`
- `vault/Dashboard.md`

### Session 2: Backend Implementation (2 hours)
**Deliverables:**
- ChatGPT API integration
- Chat endpoint with constitutional filtering
- Conversation logger
- Progress tracking endpoint
- Unit tests for backend

**Key Files:**
- `backend/routers/chat.py`
- `backend/services/chatgpt_service.py`
- `backend/services/logger_service.py`
- `tests/test_chat_endpoint.py`

### Session 3: Frontend & Integration (2 hours)
**Deliverables:**
- Next.js chat interface
- Constitutional guard component
- Course material viewer
- Progress dashboard
- Full E2E workflow

**Key Files:**
- `frontend/components/ChatInterface.tsx`
- `frontend/components/ConstitutionalGuard.tsx`
- `frontend/app/page.tsx`
- `frontend/lib/constitutionalRules.ts`

### Session 4: Testing & Validation (1.5 hours)
**Deliverables:**
- Comprehensive test suite
- Adversarial testing passed
- Documentation complete
- Completion report
- Silver tier validation

**Key Files:**
- `tests/test_constitutional_rules.py`
- `README.md`
- `COMPLETION_REPORT.md`

---

## 12. SUCCESS CRITERIA

### Bronze Tier (Minimum)
- [ ] ChatGPT integration functional
- [ ] Constitutional rules enforced 100%
- [ ] Basic chat works
- [ ] Conversations logged
- [ ] HITL queue operational
- [ ] All tests passing

### Silver Tier (Target)
- [ ] All Bronze requirements
- [ ] Multi-turn conversations
- [ ] Progress tracking
- [ ] Course materials viewer
- [ ] Learning analytics
- [ ] Response rating system

### Gold Tier (Stretch)
- [ ] All Silver requirements
- [ ] Multi-student support
- [ ] Advanced analytics
- [ ] LMS integration
- [ ] Mobile responsive
- [ ] Deployment ready

---

## 13. RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Constitutional rules bypassed | Medium | Critical | Triple-layer enforcement + adversarial testing |
| API costs exceed budget | Low | Medium | Rate limiting + caching + gpt-3.5-turbo |
| Frontend complexity | Medium | Medium | Use shadcn/ui, keep simple |
| Testing insufficient | Low | High | Comprehensive test plan + adversarial tests |
| HITL queue overwhelming | Low | Low | Conservative flagging, clear guidelines |

---

## 14. DEPENDENCIES

### Required
- OpenAI API key ($10-20 budget)
- Python 3.11+
- Node.js 18+
- npm/yarn

### Optional
- Obsidian (for vault visualization)
- Docker (for deployment)

---

## 15. ESTIMATED COSTS

**Development:**
- ChatGPT API testing: $5-10
- Total development time: 7 hours

**Production (Monthly):**
- API usage (moderate): $20-50
- Hosting: $0 (local) or $5 (cloud)

---

## 16. NEXT STEPS

**Week 2 Monday:**
1. Paste Session 1 prompt into Claude Code
2. Complete foundation in 1.5 hours
3. Verify constitutional rules enforced

**Week 2 Tuesday:**
1. Session 2: Backend (2 hours)
2. Session 3: Frontend (2 hours)
3. Test E2E workflow

**Week 2 Wednesday:**
1. Session 4: Testing & Validation (1.5 hours)
2. Submit H1 to hackathon
3. Begin H2 planning

---

**Specification Complete**  
**Author:** Asadullah Shafique  
**Date:** 2026-01-23  
**Status:** Ready for Implementation