# HITL Approval Manager Skill

**Purpose:** Manage Human-in-the-Loop approval workflow for critical AI CTO decisions

**When to use:** When the AI needs human approval before executing actions

---

## Core Workflow

### Step 1: Create Approval Request

**Location:** `vault/Pending_Approval/APPROVAL_{timestamp}_{action}.md`

**Template:**
```markdown
# APPROVAL REQUEST: [Action Type]

**Created:** [Timestamp]
**Priority:** [High/Medium/Low]
**Estimated Impact:** [Description]

## Proposed Action
[What the AI wants to do]

## Rationale
[Why this action is needed]

## Risks
[Potential downsides]

## Alternatives Considered
[Other options]

---

**Human Decision:**
- [ ] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
[Human comments here]
```

### Step 2: Monitor for Decision

**Check:** Every 30 seconds

**Look For:**
- Checkbox marked (APPROVE/REJECT/MODIFY)
- Feedback provided

### Step 3: Execute Based on Decision

**If APPROVED:**
1. Move file to `Approved/`
2. Execute the action
3. Log result
4. Update dashboard

**If REJECTED:**
1. Move file to `Rejected/`
2. Log rejection
3. Update dashboard
4. Do NOT execute action

**If MODIFIED:**
1. Read feedback
2. Adjust proposal
3. Create new approval request
4. Repeat workflow

---

## Usage Examples

### Example 1: Deploy Hackathon

```markdown
# APPROVAL REQUEST: Deploy H1 to Production

**Created:** 2026-01-28 14:30:00
**Priority:** High
**Estimated Impact:** H1 will be publicly accessible

## Proposed Action
Deploy Course Companion FTE (H1) to Railway production environment

## Rationale
- All tests passing (100% coverage)
- Spec requirements met
- Ready for submission

## Risks
- Potential production bugs
- Railway usage costs
- Public exposure

## Alternatives Considered
1. Deploy to staging first (slower)
2. Wait for more testing (delays submission)

---

**Human Decision:**
- [x] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
Looks good! Deploy to production.
```

### Example 2: Create New Spec

```markdown
# APPROVAL REQUEST: Generate H3 Specification

**Created:** 2026-02-01 10:00:00
**Priority:** Medium
**Estimated Impact:** New spec for Advanced Todo hackathon

## Proposed Action
Use Spec Generator to create SPEC-H3-ADVANCED-TODO.md

## Rationale
- H2 completed successfully
- Ready to start H3
- Spec needed for implementation

## Risks
- May miss requirements
- Token usage (~8K tokens)

## Alternatives Considered
1. Manual spec writing (slower, less consistent)
2. Reuse H2 spec (inappropriate, different requirements)

---

**Human Decision:**
- [x] ✅ APPROVE - Proceed with action
- [ ] ❌ REJECT - Do not proceed
- [ ] 🔄 MODIFY - Adjust and resubmit

**Feedback:**
Approved. Generate the spec.
```

---

## Implementation Notes

**File Naming:**
`APPROVAL_{YYYYMMDD}_{HHMMSS}_{action_type}.md`

**Priority Levels:**
- **High:** Production deployments, external communications, spending money
- **Medium:** Creating specs, modifying code, data operations
- **Low:** Documentation updates, dashboard changes

**Response Time Expectations:**
- High priority: Review within 1 hour
- Medium priority: Review within 4 hours
- Low priority: Review within 24 hours

---

_This workflow ensures human oversight while maintaining AI autonomy for routine tasks._