# Architecture Template

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      {{SYSTEM_NAME}}                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Component  │  │  Component  │  │  Component  │         │
│  │      A      │─▶│      B      │─▶│      C      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Component A: {{COMPONENT_A_NAME}}
**Responsibility:** {{COMPONENT_A_RESPONSIBILITY}}

**Inputs:**
- {{INPUT_1}}
- {{INPUT_2}}

**Outputs:**
- {{OUTPUT_1}}
- {{OUTPUT_2}}

**Key Functions:**
- `{{FUNCTION_1}}()`: {{DESCRIPTION}}
- `{{FUNCTION_2}}()`: {{DESCRIPTION}}

---

## Data Flow

```
{{DATA_SOURCE}} → {{PROCESS_1}} → {{PROCESS_2}} → {{OUTPUT}}
```

## Technology Stack

| Layer          | Technology      | Purpose                |
|----------------|-----------------|------------------------|
| {{LAYER_1}}    | {{TECH_1}}      | {{PURPOSE_1}}          |
| {{LAYER_2}}    | {{TECH_2}}      | {{PURPOSE_2}}          |

## Integration Points

- **External API:** {{API_DESCRIPTION}}
- **Database:** {{DB_DESCRIPTION}}
- **Cache:** {{CACHE_DESCRIPTION}}
