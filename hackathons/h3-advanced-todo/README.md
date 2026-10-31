# H3 Advanced Todo Application

A full-featured todo application with Constitutional AI validation, team collaboration, AI suggestions, calendar integration, and more.

## Gold Tier Achievement

**149 Tests Passing** | Constitutional AI | Team Collaboration | AI Suggestions | Calendar Sync

---

## Overview

The H3 Advanced Todo Application is a sophisticated task management system featuring team collaboration, AI-powered suggestions, calendar integration, and advanced productivity tools. Built with Next.js, Tailwind CSS, and FastAPI, it provides a comprehensive solution for personal and team task management.

---

## Features

### Core Features
- **Todo CRUD**: Create, read, update, delete todos with categories and priorities
- **Constitutional AI Validation**: Blocks prohibited content (academic dishonesty, hacking, etc.)
- **Statistics Dashboard**: Track completion rates and productivity

### Recurring Todos
- **Daily Patterns**: Repeat todos every day
- **Weekly Patterns**: Repeat on specific days of the week
- **Monthly Patterns**: Repeat on specific day of month
- **Custom Intervals**: Define custom repetition intervals

### Templates
- **Built-in Templates**: Pre-configured task templates
- **Custom Templates**: Create your own reusable task templates
- **Template Preview**: Preview todos before creation
- **Usage Tracking**: Track template popularity

### Team Collaboration
- **Team Management**: Create and manage teams
- **Role-Based Access**: Owner, Admin, Editor, Viewer roles
- **Member Management**: Add, remove, update member roles
- **Team Todos**: Shared todos within teams
- **Comments**: Discuss todos with team members

### Todo Assignments
- **Assign Todos**: Assign tasks to team members
- **Status Tracking**: Track assignment progress (assigned, accepted, in_progress, completed, declined)
- **Due Dates**: Set assignment deadlines
- **Notes**: Add context to assignments

### AI Suggestions
- **Smart Suggestions**: AI-powered recommendations for todos
- **Insights**: Productivity insights and patterns
- **Actionable Items**: Apply suggestions with one click
- **Suggestion Types**: Priority, breakdown, recurring, deadline, category

### Calendar Integration
- **Multi-Provider**: Google, Outlook, Apple calendar support
- **OAuth Flow**: Secure calendar connection
- **Sync Options**: Todo-to-calendar, calendar-to-todo, bidirectional
- **Event Management**: Create, view, delete calendar events

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLAlchemy ORM with SQLite
- **Validation**: Pydantic schemas
- **Testing**: pytest with 149 tests

### Frontend
- **Framework**: Next.js 14 (React)
- **State Management**: Zustand
- **Styling**: Tailwind CSS
- **Components**: Custom UI with Lucide icons

---

## Project Structure

```
h3-advanced-todo/
├── backend/
│   ├── main.py              # FastAPI application entry
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── todo.py          # Todo model
│   │   ├── recurring_todo.py # Recurring todo model
│   │   ├── template.py      # Template model
│   │   ├── user.py          # User model
│   │   ├── team.py          # Team & member models
│   │   ├── assignment.py    # Assignment model
│   │   ├── suggestion.py    # AI suggestion model
│   │   └── calendar.py      # Calendar connection model
│   ├── routers/             # API route handlers
│   │   ├── todos.py         # Todo CRUD endpoints
│   │   ├── recurring.py     # Recurring todo endpoints
│   │   ├── templates.py     # Template endpoints
│   │   ├── users.py         # User endpoints
│   │   ├── teams.py         # Team & member endpoints
│   │   ├── assignments.py   # Assignment endpoints
│   │   ├── suggestions.py   # AI suggestion endpoints
│   │   ├── calendar.py      # Calendar endpoints
│   │   └── stats.py         # Statistics endpoints
│   ├── services/            # Business logic
│   │   ├── constitutional_validator.py  # Content validation
│   │   ├── recurring_service.py         # Recurring logic
│   │   ├── team_service.py              # Team operations
│   │   ├── suggestion_service.py        # AI suggestions
│   │   └── calendar_service.py          # Calendar sync
│   └── tests/               # Test suite (149 tests)
│       ├── conftest.py      # Shared fixtures
│       ├── test_constitutional.py
│       ├── test_crud.py
│       ├── test_recurring.py
│       ├── test_templates.py
│       ├── test_users.py
│       ├── test_teams.py
│       ├── test_assignments.py
│       ├── test_suggestions.py
│       └── test_calendar.py
├── frontend/
│   ├── app/
│   │   └── page.tsx         # Main page with tabs
│   ├── components/
│   │   ├── AISuggestions.tsx
│   │   ├── CalendarIntegration.tsx
│   │   ├── TeamSelector.tsx
│   │   ├── TeamMembersList.tsx
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── store.ts         # Zustand store
│   │   └── types.ts         # TypeScript types
│   └── package.json
├── INTEGRATION_TEST_CHECKLIST.md
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend
cd hackathons/h3-advanced-todo/backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
# Navigate to frontend
cd hackathons/h3-advanced-todo/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# App available at http://localhost:3000
```

### Run Tests

```bash
# Navigate to backend
cd hackathons/h3-advanced-todo/backend

# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ -v --cov=. --cov-report=html
```

---

## API Reference

### Todos
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/todos | List all todos |
| POST | /api/todos | Create a todo |
| GET | /api/todos/{id} | Get a todo |
| PUT | /api/todos/{id} | Update a todo |
| DELETE | /api/todos/{id} | Delete a todo |
| GET | /api/stats | Get statistics |

### Recurring Todos
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/recurring | List recurring patterns |
| POST | /api/recurring | Create recurring pattern |
| GET | /api/recurring/{id} | Get pattern details |
| POST | /api/recurring/{id}/generate | Generate occurrence |
| GET | /api/recurring/{id}/preview | Preview occurrences |
| DELETE | /api/recurring/{id} | Delete pattern |

### Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/templates | List templates |
| POST | /api/templates | Create template |
| GET | /api/templates/{id} | Get template |
| POST | /api/templates/{id}/use | Use template |
| GET | /api/templates/{id}/preview | Preview template |
| DELETE | /api/templates/{id} | Delete template |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users | List users |
| POST | /api/users | Create user |
| GET | /api/users/{id} | Get user |
| PUT | /api/users/{id} | Update user |
| GET | /api/users/{id}/assignments | Get user's assignments |

### Teams
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/teams | List user's teams |
| POST | /api/teams | Create team |
| GET | /api/teams/{id} | Get team |
| PUT | /api/teams/{id} | Update team |
| DELETE | /api/teams/{id} | Delete team |
| GET | /api/teams/{id}/members | List members |
| POST | /api/teams/{id}/members | Add member |
| PUT | /api/teams/{id}/members/{user_id} | Update role |
| DELETE | /api/teams/{id}/members/{user_id} | Remove member |
| GET | /api/teams/{id}/todos | List team todos |

### Assignments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/todos/{id}/assign | Assign todo |
| GET | /api/todos/{id}/assignments | Get todo assignments |
| PUT | /api/assignments/{id} | Update assignment |
| DELETE | /api/assignments/{id} | Remove assignment |

### AI Suggestions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/suggestions | List suggestions |
| POST | /api/suggestions/generate/{todo_id} | Generate for todo |
| POST | /api/suggestions/insights/{user_id} | Generate insights |
| PUT | /api/suggestions/{id} | Update suggestion |
| POST | /api/suggestions/{id}/apply | Apply suggestion |
| DELETE | /api/suggestions/{id} | Delete suggestion |

### Calendar
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/calendar/connect/{provider} | Initiate connection |
| POST | /api/calendar/callback/{id} | Complete OAuth |
| GET | /api/calendar/connections | List connections |
| GET | /api/calendar/connections/{id} | Get connection |
| PUT | /api/calendar/connections/{id}/settings | Update settings |
| DELETE | /api/calendar/connections/{id} | Disconnect |
| GET | /api/calendar/events | List events |
| POST | /api/calendar/events | Create event |
| DELETE | /api/calendar/events/{id} | Delete event |
| POST | /api/calendar/sync | Sync all todos |
| POST | /api/calendar/sync/{todo_id} | Sync single todo |

---

## Constitutional AI

The application uses Constitutional AI to ensure todos are ethical and appropriate:

### Blocked Content
- Academic dishonesty (homework completion, exam answers)
- Hacking and security exploits
- Cheating and plagiarism
- Fraudulent document creation
- Harassment content

### Allowed Content
- Study and learning tasks
- Work-related tasks
- Personal development
- Exercise and health
- Research and exploration

### Flagged Content
- Content marked as urgent (reviewed but allowed)
- Time-sensitive items

---

## Team Roles

| Role | Create Todos | Edit Todos | Manage Members | Delete Team |
|------|-------------|------------|----------------|-------------|
| Owner | Yes | Yes | Yes | Yes |
| Admin | Yes | Yes | Yes | No |
| Editor | Yes | Yes | No | No |
| Viewer | No | No | No | No |

---

## Development Sessions

### Session 1: Core + Recurring + Templates
- Constitutional AI validation
- CRUD operations
- Recurring todo patterns
- Template system

### Session 2: Team Collaboration
- User management
- Team creation
- Role-based permissions
- Todo assignments

### Session 3: AI + Calendar
- AI suggestion engine
- User insights
- Calendar integration (Google/Outlook/Apple)
- Todo-calendar sync

### Session 4: Integration & Gold Tier
- 149 comprehensive tests
- Integration test checklist
- Full documentation

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + N | Create new todo |
| Ctrl + Shift + N | Create new team |
| Ctrl + E | Edit selected todo |
| Ctrl + D | Delete selected todo |
| Ctrl + K | Show keyboard shortcuts |

---

## License

MIT License

---

*Built for Hackathon H3 - Gold Tier Achieved*
