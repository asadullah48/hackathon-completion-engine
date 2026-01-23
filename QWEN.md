# Hackathon Completion Engine - QWEN.md

## Project Overview

The Hackathon Completion Engine is a universal framework designed to systematically complete 5 Panaversity hackathons in 3 weeks using spec-driven development. The project follows a constitutional approach with strict principles around reusability, token optimization, and validation-first development.

### Core Purpose
- Complete all 5 hackathons with Gold tier minimum scoring
- Demonstrate business project readiness through systematic, reusable architecture
- Transform undefined problems into defined, spec-driven solutions
- Prove framework scalability and reusability

### Architecture Pattern
```
Universal Engine (Core)
    ↓
Hackathon Templates (Adapters)
    ↓
Specific Implementations (Instances)
```

## Project Structure

```
D:\Personal-AI-Employee\
├── CONSTITUTION.md              # Project-wide constitutional rules
├── engine/                      # Universal framework
│   ├── spec-generator/          # Auto-generate specs
│   ├── skill-mapper/            # Map skills to requirements
│   ├── template-system/         # Project templates
│   └── deployment-automator/    # One-click deploy
├── hackathons/                  # All 5 hackathons
│   ├── h0-personal-ai-cto/      # Hackathon 0 - Personal AI CTO
│   ├── h1-course-companion/     # Hackathon 1 - Course Companion FTE
│   ├── h2-todo-spec-driven/     # Hackathon 2 - Todo Spec-Driven
│   ├── h3-advanced-todo/        # Hackathon 3 - Advanced Todo
│   └── h4-cloud-deployment/     # Hackathon 4 - Cloud Deployment
├── skills-library/              # 39+ Agent Skills
├── specs/                       # All specification documents
└── .claude/                     # Claude Code configuration
```

## Core Principles

1. **Spec-Driven Development**: No code exists without a spec first
2. **Token Optimization**: Minimize API costs ruthlessly
3. **Reusability First**: Build once, adapt many times
4. **39+ Agent Skills Leverage**: Use existing skills before creating new ones
5. **Validation-First Development**: Every component must have clear validation criteria

## Key Components

### Engine Components
- **Spec Generator**: Auto-generates specifications from hackathon descriptions
- **Skill Mapper**: Maps requirements to existing agent skills
- **Template System**: Provides project templates
- **Deployment Automator**: Handles one-click deployments

### Hackathon 0: Personal AI CTO
- **Purpose**: Meta-system that manages other hackathons
- **Features**:
  - File system watcher monitoring `D:\AI-Employee-Inbox`
  - Obsidian vault for knowledge management
  - Human-in-the-Loop (HITL) approval workflow
  - Dashboard for real-time status tracking
  - Activity logging system

## Building and Running

### Prerequisites
- Python 3.11+
- Pip package manager

### Setup
```bash
# Clone or navigate to project directory
cd /path/to/Personal-AI-Employee

# Create virtual environment (if not already created)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System
```bash
# Activate virtual environment
source venv/bin/activate

# Run the file watcher for H0 Personal AI CTO
cd hackathons/h0-personal-ai-cto
python watchers/file_watcher.py --vault ./vault --drop-folder "D:\AI-Employee-Inbox" --interval 10
```

### CLI Commands
The project includes several CLI tools defined in pyproject.toml:
- `hce-spec`: Generate specifications
- `hce-map`: Map skills to requirements
- `hce-template`: Generate project templates
- `hce-deploy`: Handle deployments

## Development Conventions

### File Naming
- Specs: `SPEC-{hackathon}-{feature}.md` (e.g., `SPEC-H0-file-watcher.md`)
- Constitutions: `CONSTITUTION-{hackathon}.md`
- Implementation: Follow language conventions (snake_case Python)

### Commit Format
- Format: `[H{N}] {type}: {description}`
- Types: feat, fix, docs, refactor, test, chore
- Example: `[H0] feat: implement file watcher`

### Documentation Standards
- High density for reusable components
- Medium for hackathon-specific code
- Low for standard implementations

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run tests with verbose output
python -m pytest tests/ -v
```

### Test Structure
- Unit tests for individual components
- Integration tests for system workflows
- Validation tests for spec compliance

## Claude Code Configuration

The project is configured for Claude Code with appropriate permissions for:
- File system operations
- Python execution
- Package installation
- Git operations
- Web fetching for documentation

## Success Metrics

### Per Hackathon
- Gold tier achievement (minimum acceptable)
- Implementation time ≤ allocated budget
- Token usage ≤ 50K per hackathon
- Code reusability ≥ 60%

### Overall
- All 5 hackathons complete in 21 days
- Total token usage ≤ 250K
- Framework reusability proven
- Business readiness demonstrated

## Security & Compliance

- Never commit API keys or passwords
- Use .env for all secrets
- Explicit MCP permissions allow-list
- No user data in logs or specs
- Follow all Panaversity guidelines
- Maintain academic integrity

## Operational Workflow

### Daily Process
1. Review dashboard, prioritize tasks
2. Spec Creation: Write specs for day's work
3. Execution: Claude Code implements specs
4. Validation: Verify all outputs
5. Evening: Update progress, plan tomorrow

### Quality Gates
- All specs written and reviewed
- Claude Code implementation complete
- Validation criteria met
- Documentation updated
- Integration tests passing

This project represents a systematic approach to hackathon completion using AI-assisted development with strict governance and validation processes.