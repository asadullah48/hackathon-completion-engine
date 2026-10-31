# SPEC-H3-CORE: Advanced Todo Features
**Building on H2 Foundation for Gold Tier**

**Version:** 1.0  
**Date:** 2026-01-25  
**Target Tier:** Gold  
**Estimated Time:** 8-10 hours  
**Reuses from H2:** 85%

---

## 1. OVERVIEW

### Purpose
H3 extends H2 (AI-Powered Todo App) with advanced features to achieve Gold tier certification. Builds directly on H2's Zero-Backend-LLM architecture and constitutional enforcement.

### Core Innovation
**Intelligent Automation Layer** - Adds recurring todos, templates, AI-powered suggestions, and team collaboration while maintaining constitutional compliance.

### Key Differentiator
Unlike basic todo apps, H3 combines:
- **Recurring tasks** with intelligent scheduling
- **Smart templates** with AI customization
- **Team collaboration** with role-based access
- **AI suggestions** based on usage patterns
- **Calendar integration** for unified workflow

---

## 2. ARCHITECTURE (EXTENDS H2)
```
H3 = H2 + Advanced Features

┌─────────────────────────────────────┐
│   Frontend (Next.js)                │
│  ┌──────────────────────────────┐   │
│  │ NEW: Advanced Features       │   │
│  │ • Recurring task engine      │   │
│  │ • Template system            │   │
│  │ • AI suggestions             │   │
│  │ • Team collaboration UI      │   │
│  │ • Calendar sync              │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ FROM H2: Base Features       │   │
│  │ • AI parsing                 │   │
│  │ • Constitutional filter      │   │
│  │ • CRUD operations            │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Backend (FastAPI)                 │
│  ┌──────────────────────────────┐   │
│  │ NEW: Advanced Models         │   │
│  │ • RecurringTodo              │   │
│  │ • Template                   │   │
│  │ • Team, TeamMember           │   │
│  │ • Suggestion                 │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ FROM H2: Base Models         │   │
│  │ • Todo (enhanced)            │   │
│  │ • Constitutional validator   │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   New: Calendar Integration         │
│  • Google Calendar API              │
│  • Microsoft Outlook API            │
│  • Two-way sync                     │
└─────────────────────────────────────┘
```

---

## 3. NEW FEATURES (GOLD TIER)

### Feature 1: Recurring Todos ⚡

**Patterns:**
- Daily (every day, weekdays, weekends)
- Weekly (specific days: Mon/Wed/Fri)
- Monthly (specific date, first Monday, last Friday)
- Custom (every N days, complex patterns)

**Smart Scheduling:**
- Auto-generate next occurrence
- Skip holidays (optional)
- Adjust for weekends
- Handle missed occurrences

**UI:**
- Recurrence pattern selector
- Visual calendar preview
- History of completed occurrences
- Skip/reschedule options

**Example:**
```
"Exercise" → Repeats: Daily at 7am
"Team standup" → Repeats: Weekdays at 9am
"Monthly report" → Repeats: Last Friday of month
```

---

### Feature 2: Todo Templates 📋

**Template Types:**
- Personal (exercise routine, meal prep)
- Work (project kickoff, code review)
- Study (exam prep, assignment workflow)
- Custom (user-created)

**Template Features:**
- Pre-filled todos with subtasks
- Category, priority, deadlines pre-set
- Customizable fields
- AI-enhanced suggestions
- Share with team

**Template Library:**
- 10+ built-in templates
- Community templates (future)
- Template versioning
- Usage analytics

**Example Template: "Project Kickoff"**
```json
{
  "name": "Project Kickoff",
  "category": "work",
  "todos": [
    {"title": "Define project scope", "priority": "high"},
    {"title": "Create timeline", "priority": "high"},
    {"title": "Assign team roles", "priority": "medium"},
    {"title": "Set up repo", "priority": "medium"},
    {"title": "Schedule kickoff meeting", "priority": "high"}
  ]
}
```

---

### Feature 3: Team Collaboration 👥

**Team Features:**
- Create teams (max 10 members for demo)
- Assign todos to team members
- Shared todo lists
- Activity feed (who did what)
- Comments on todos
- @mentions in comments

**Permissions:**
- Owner (full control)
- Admin (manage members, edit all)
- Member (edit assigned, view all)
- Viewer (read-only)

**Constitutional Compliance:**
- Team todos also validated
- Block shared homework help
- Flag suspicious team activities

**UI:**
- Team dashboard
- Member management
- Assignment view
- Activity timeline

---

### Feature 4: AI Suggestions 🤖

**Suggestion Types:**

**1. Priority Suggestions:**
- "Based on deadlines, consider making 'Client presentation' high priority"
- "You have 3 overdue tasks, want to reschedule?"

**2. Task Breakdown:**
- "Large task detected: 'Complete project'. Break into subtasks?"
- Suggests: Planning, Development, Testing, Deployment

**3. Pattern Recognition:**
- "You often create 'Exercise' todos. Make it recurring?"
- "You usually work on coding in mornings. Optimal time?"

**4. Productivity Insights:**
- "You've completed 80% of 'study' tasks this week! 🎉"
- "Your 'high priority' completion rate: 60%. Focus more?"

**Implementation:**
- Analyze user history
- GPT-4 for intelligent suggestions
- User can accept/dismiss
- Learn from user preferences

---

### Feature 5: Calendar Integration 📅

**Supported Calendars:**
- Google Calendar
- Microsoft Outlook
- Apple Calendar (future)

**Features:**
- Two-way sync
- Create calendar events from todos with deadlines
- Update todos when calendar events change
- Show calendar availability in todo app
- Visual timeline view

**Sync Rules:**
- Only sync todos with deadlines
- Respect constitutional rules (no blocked todos synced)
- Handle conflicts (user chooses)
- Offline queue (sync when online)

**UI:**
- Calendar authorization flow
- Sync settings panel
- Visual calendar view
- Conflict resolution UI

---

## 4. ENHANCED DATA MODELS

### RecurringTodo Model
```typescript
interface RecurringTodo {
  id: string;
  pattern: 'daily' | 'weekly' | 'monthly' | 'custom';
  interval: number; // Every N days/weeks/months
  days_of_week?: number[]; // [0=Sun, 1=Mon, ...]
  day_of_month?: number; // 1-31
  end_date?: Date;
  last_generated?: Date;
  next_occurrence?: Date;
  skip_holidays: boolean;
  template_todo_id: string; // Base todo to clone
}
```

### Template Model
```typescript
interface Template {
  id: string;
  name: string;
  description: string;
  category: TodoCategory;
  todos: TemplateTodo[];
  created_by: string;
  is_public: boolean;
  usage_count: number;
  created_at: Date;
}

interface TemplateTodo {
  title: string;
  description?: string;
  category: TodoCategory;
  priority: TodoPriority;
  relative_deadline?: number; // Days from creation
}
```

### Team Models
```typescript
interface Team {
  id: string;
  name: string;
  description: string;
  created_by: string;
  created_at: Date;
}

interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joined_at: Date;
}

interface TeamTodo extends Todo {
  team_id: string;
  assigned_to?: string;
  comments: Comment[];
}

interface Comment {
  id: string;
  todo_id: string;
  user_id: string;
  content: string;
  created_at: Date;
}
```

### Suggestion Model
```typescript
interface Suggestion {
  id: string;
  type: 'priority' | 'breakdown' | 'recurring' | 'insight';
  content: string;
  action_payload?: object;
  dismissed: boolean;
  created_at: Date;
}
```

---

## 5. NEW API ENDPOINTS

### Recurring Todos
```
POST   /api/recurring          - Create recurring pattern
GET    /api/recurring          - List all recurring todos
PUT    /api/recurring/{id}     - Update pattern
DELETE /api/recurring/{id}     - Delete pattern
POST   /api/recurring/{id}/generate - Manually generate next occurrence
```

### Templates
```
GET    /api/templates          - List templates
GET    /api/templates/{id}     - Get template
POST   /api/templates          - Create template
POST   /api/templates/{id}/use - Create todos from template
DELETE /api/templates/{id}     - Delete template
```

### Teams
```
POST   /api/teams              - Create team
GET    /api/teams              - List user's teams
POST   /api/teams/{id}/members - Add member
DELETE /api/teams/{id}/members/{user_id} - Remove member
GET    /api/teams/{id}/todos   - Get team todos
```

### Suggestions
```
GET    /api/suggestions        - Get pending suggestions
POST   /api/suggestions/{id}/accept - Accept suggestion
POST   /api/suggestions/{id}/dismiss - Dismiss suggestion
```

### Calendar
```
POST   /api/calendar/auth      - Initiate OAuth flow
GET    /api/calendar/sync      - Trigger sync
GET    /api/calendar/events    - Get calendar events
```

---

## 6. REUSABILITY FROM H2

| Component | H2 Implementation | H3 Usage | Reuse % |
|-----------|------------------|----------|---------|
| Todo Model | Complete | Enhanced with team_id, recurring_id | 95% |
| Constitutional Filter | Complete | Applied to templates, team todos | 100% |
| AI Parser | Complete | Used for suggestion generation | 90% |
| FastAPI Backend | Complete | Add new routers | 85% |
| Next.js Frontend | Complete | Add new components | 80% |
| Zustand Store | Complete | Extend for new features | 90% |
| Testing Framework | Complete | Add new test suites | 100% |
| UI Components | Complete | Enhance and extend | 85% |

**Overall Reuse:** ~85% from H2

---

## 7. FOUR-SESSION IMPLEMENTATION

### Session 1: Recurring Todos & Templates (2.5 hours)

**Backend:**
- RecurringTodo model
- Template model
- Recurring router
- Template router
- Generation logic (cron-like)

**Frontend:**
- RecurringPattern selector
- Template library UI
- Template creator
- Recurrence schedule viewer

**Tests:**
- Recurring pattern generation
- Template CRUD
- Schedule calculations

---

### Session 2: Team Collaboration (2.5 hours)

**Backend:**
- Team, TeamMember models
- Comment model
- Team router
- Assignment logic
- Activity feed

**Frontend:**
- Team dashboard
- Member management UI
- Assignment picker
- Comment system
- Activity timeline

**Tests:**
- Team CRUD
- Member permissions
- Comments

---

### Session 3: AI Suggestions & Calendar (2.5 hours)

**Backend:**
- Suggestion model
- Suggestion generator service
- Calendar integration (Google/Outlook OAuth)
- Sync service

**Frontend:**
- Suggestion cards UI
- Calendar auth flow
- Calendar sync settings
- Visual calendar view

**Tests:**
- Suggestion generation
- Calendar sync logic

---

### Session 4: Integration & Polish (2.5 hours)

**Tasks:**
- E2E testing all features
- Performance optimization
- UI polish and animations
- Comprehensive documentation
- Gold tier validation

---

## 8. GOLD TIER SUCCESS CRITERIA

### Must Have (Gold Baseline)
- [ ] Recurring todos working (daily, weekly, monthly)
- [ ] At least 5 usable templates
- [ ] Team collaboration (2+ members)
- [ ] Assignment and comments
- [ ] AI suggestions (3+ types)
- [ ] Calendar integration (Google or Outlook)
- [ ] All constitutional rules enforced
- [ ] All Silver tier features still working

### Should Have (Gold+)
- [ ] 10+ templates
- [ ] Advanced recurrence patterns
- [ ] Rich text comments
- [ ] Two-way calendar sync
- [ ] Productivity analytics
- [ ] Mobile responsive (all features)

### Nice to Have (Platinum)
- [ ] Voice commands
- [ ] Offline mode (PWA)
- [ ] Real-time collaboration
- [ ] Advanced AI insights
- [ ] Multi-language support

---

## 9. TECHNICAL CHALLENGES

### Challenge 1: Recurring Logic Complexity
**Solution:** Use `dateutil` (Python) and `date-fns` (TypeScript)

### Challenge 2: Calendar OAuth
**Solution:** Use OAuth2 libraries, secure token storage

### Challenge 3: Team Real-time Updates
**Solution:** Polling (simple) or WebSockets (advanced)

### Challenge 4: AI Suggestion Quality
**Solution:** Pattern analysis + GPT-4, user feedback loop

---

## 10. DEPENDENCIES

**New Python Packages:**
```
python-dateutil==2.8.2
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-api-python-client==2.110.0
msal==1.25.0  # Microsoft auth
```

**New JavaScript Packages:**
```
date-fns
@react-oauth/google
@azure/msal-browser
react-big-calendar
```

---

## 11. ESTIMATED TIMELINE

**Session 1:** 2.5 hours (Recurring + Templates)  
**Session 2:** 2.5 hours (Teams)  
**Session 3:** 2.5 hours (AI + Calendar)  
**Session 4:** 2.5 hours (Integration)  
**Total:** 10 hours

**With breaks:** 1.5 days

---

## 12. NEXT STEPS AFTER H3

**H4: Cloud Deployment**
- Deploy H3 to production
- Kubernetes configuration
- CI/CD pipeline
- Monitoring & scaling
- Multi-user support

**H5: Analytics & Insights** (Optional)
- Advanced productivity analytics
- Team performance metrics
- AI-powered insights dashboard
- Predictive task completion

---

**Specification Status:** ✅ Complete  
**Ready for:** Session 1 execution  
**Author:** Asadullah Shafique  
**Date:** 2026-01-25  
**Prerequisites:** H2 complete