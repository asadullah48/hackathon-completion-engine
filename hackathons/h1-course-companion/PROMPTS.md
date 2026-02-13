# H1 IMPLEMENTATION PROMPTS
**Ready-to-paste prompts for Claude Code**

---

## SESSION 1 PROMPT: Foundation (1.5 hours)
```
IMPLEMENTATION: H1 Course Companion FTE - Session 1 (Foundation)

CONTEXT:
Building an AI course companion with strict constitutional rules to prevent academic integrity violations. Reusing 60% of H0 components.

PREREQUISITES:
- H0 complete and tested
- OpenAI API key obtained
- Spec document reviewed: SPEC-H1-CORE.md

TASK 1.1: Create Directory Structure

Create: /mnt/d/Personal-AI-Employee/hackathons/h1-course-companion/

Structure:
```
h1-course-companion/
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
├── backend/
│   ├── routers/
│   ├── middleware/
│   ├── services/
│   └── models/
├── vault/
│   ├── Course_Materials/
│   ├── Student_Progress/
│   ├── Conversation_Logs/
│   ├── Pending_Approval/
│   └── Dashboard.md
├── skills/
└── tests/
```

TASK 1.2: Create Constitutional Rules Skill

Create: skills/constitutional-rules.md

Content: Complete skill document that defines:
- Absolute prohibitions (homework solutions, code writing, exam help)
- Required behaviors (Socratic questioning, concept explanation)
- Enforcement mechanisms (system prompt, middleware, frontend)
- Example scenarios (allowed vs prohibited queries)

TASK 1.3: Initialize FastAPI Backend

Create: backend/main.py

Requirements:
- FastAPI app with CORS
- Constitutional middleware integration
- Health check endpoint
- Chat router stub
- Environment variable loading

Create: backend/middleware/constitutional_filter.py

Requirements:
- Prohibited pattern detection (regex)
- Suspicious pattern flagging
- Logging all queries
- Returns: allow/block/flag decision

Create: backend/requirements.txt

Include:
- fastapi
- uvicorn
- openai
- python-dotenv
- pydantic
- aiofiles

TASK 1.4: Create Vault Structure

Copy: H0 vault structure as template
Modify: Add Course_Materials/, Student_Progress/ folders
Create: Dashboard.md for student progress tracking

TASK 1.5: Environment Configuration

Create: backend/.env.example
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=500
TEMPERATURE=0.7
VAULT_PATH=../vault
```

VALIDATION:
Show me:
1. Complete directory structure (tree view)
2. Constitutional rules skill content (first 50 lines)
3. FastAPI main.py with middleware integration
4. Constitutional filter implementation
5. Vault structure with new folders

Execute all tasks and wait for approval before Session 2.
```

---

## SESSION 2 PROMPT: Backend Implementation (2 hours)