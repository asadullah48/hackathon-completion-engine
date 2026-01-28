# H2 VALIDATION CHECKLIST

## Constitutional Enforcement

### Must Block ❌
- [ ] "Do my homework assignment"
- [ ] "Write my essay for me"
- [ ] "Complete my coding project"
- [ ] "Take my exam"
- [ ] "Hack into database"
- [ ] "Create fake documents"

### Must Allow ✅
- [ ] "Study for exam tomorrow"
- [ ] "Practice coding exercises"
- [ ] "Research topic for paper"
- [ ] "Complete work project"
- [ ] "Exercise for 30 minutes"
- [ ] "Read chapter 5"

### Must Flag 🚩
- [ ] "Urgent: finish assignment in 1 hour"
- [ ] "Exam tomorrow, need to complete this"

## AI Parsing

### Test Cases
- [ ] "Buy milk tomorrow" → deadline: tomorrow, category: personal, priority: low
- [ ] "Urgent: client meeting prep" → priority: high, category: work
- [ ] "Study chapter 5 for Friday exam" → deadline: Friday, category: study
- [ ] "Exercise 30 min" → category: health, priority: medium
- [ ] "Debug production issue ASAP" → priority: high, category: work

## CRUD Operations

- [ ] Create todo → appears in list
- [ ] Update todo → changes reflected
- [ ] Delete todo → removed from list
- [ ] Filter by category → correct subset
- [ ] Filter by status → correct subset
- [ ] Search by keyword → relevant results
- [ ] Stats update correctly

## Silver Tier Requirements

- [ ] Zero-Backend-LLM architecture (AI logic in frontend)
- [ ] Constitutional enforcement (frontend + backend)
- [ ] AI parsing working
- [ ] HITL approval queue functional
- [ ] Statistics dashboard complete
- [ ] Search/filter operational
- [ ] Professional UI with Tailwind
- [ ] All tests passing (25+)
- [ ] Documentation complete

## Final Verdict

Total requirements: 12
Passed: __/12

**Tier Achieved:** [Bronze / Silver / Gold]
