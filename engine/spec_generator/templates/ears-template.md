# EARS (Easy Approach to Requirements Syntax) Templates

## Pattern Reference

### Ubiquitous Requirements
**Format:** The [system] SHALL [action]
**Example:** The system SHALL encrypt all stored passwords.

### Event-Driven Requirements
**Format:** WHEN [trigger], the [system] SHALL [action]
**Example:** WHEN a user submits invalid credentials, the system SHALL display an error message.

### Unwanted Behavior Requirements
**Format:** IF [unwanted condition], THEN the [system] SHALL [mitigation]
**Example:** IF the database connection fails, THEN the system SHALL retry up to 3 times.

### State-Driven Requirements
**Format:** WHILE [state], the [system] SHALL [action]
**Example:** WHILE in maintenance mode, the system SHALL reject new connections.

### Optional Requirements
**Format:** WHERE [feature is included], the [system] SHALL [action]
**Example:** WHERE multi-factor authentication is enabled, the system SHALL require a second verification step.

### Complex Requirements
**Format:** WHILE [state], WHEN [trigger], the [system] SHALL [action]
**Example:** WHILE the user is logged in, WHEN they click logout, the system SHALL terminate the session.

---

## Template Structure

**REQ-{{ID}}:** {{EARS_PATTERN}} the system SHALL {{ACTION}}.

**Acceptance Criteria:**
- [ ] {{CRITERIA_1}}
- [ ] {{CRITERIA_2}}

**Priority:** {{PRIORITY}} (Critical/High/Medium/Low)

**Dependencies:** {{DEPENDENCIES}}
