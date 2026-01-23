"""
Spec Formatter - Format parsed descriptions into spec documents.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .parser import ParsedDescription, ParsedRequirement


class SpecFormatter:
    """Format parsed descriptions into specification documents."""

    EARS_PATTERNS = {
        "ubiquitous": "The {system} SHALL {action}.",
        "event_driven": "WHEN {trigger}, the {system} SHALL {action}.",
        "unwanted": "IF {condition}, THEN the {system} SHALL {mitigation}.",
        "state_driven": "WHILE {state}, the {system} SHALL {action}.",
        "optional": "WHERE {feature}, the {system} SHALL {action}.",
    }

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self._load_templates()

    def _load_templates(self):
        """Load spec templates."""
        self.base_template = self._read_template("base-spec.md")
        self.ears_template = self._read_template("ears-template.md")
        self.arch_template = self._read_template("architecture-template.md")

    def _read_template(self, name: str) -> str:
        """Read a template file."""
        path = self.templates_dir / name
        if path.exists():
            return path.read_text()
        return ""

    def format_spec(
        self,
        parsed: ParsedDescription,
        author: str = "Asadullah",
        version: str = "1.0.0",
    ) -> str:
        """Format a parsed description into a full spec document."""

        # Format each section
        functional_reqs = self._format_requirements(
            [r for r in parsed.requirements if r.category == "functional"]
        )

        non_functional_reqs = self._format_requirements(
            [r for r in parsed.requirements if r.category == "non_functional"]
        )

        architecture = self._generate_architecture(parsed)
        implementation_plan = self._generate_implementation_plan(parsed)
        validation_criteria = self._generate_validation_criteria(parsed)
        dependencies = self._format_dependencies(parsed.technologies)

        # Build the spec document
        spec = self.base_template

        replacements = {
            "{{SPEC_NAME}}": parsed.title,
            "{{VERSION}}": version,
            "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
            "{{AUTHOR}}": author,
            "{{EFFORT}}": self._estimate_effort(parsed),
            "{{SUMMARY}}": parsed.summary,
            "{{FUNCTIONAL_REQUIREMENTS}}": functional_reqs,
            "{{NON_FUNCTIONAL_REQUIREMENTS}}": non_functional_reqs,
            "{{ARCHITECTURE}}": architecture,
            "{{IMPLEMENTATION_PLAN}}": implementation_plan,
            "{{VALIDATION_CRITERIA}}": validation_criteria,
            "{{DEPENDENCIES}}": dependencies,
        }

        for placeholder, value in replacements.items():
            spec = spec.replace(placeholder, value)

        return spec

    def _format_requirements(self, requirements: list[ParsedRequirement]) -> str:
        """Format requirements in EARS format."""
        if not requirements:
            return "*No requirements identified in this category.*"

        lines = []
        for req in requirements:
            ears_text = self._convert_to_ears(req)
            priority_badge = f"[{req.priority.upper()}]"
            lines.append(f"**{req.id}:** {priority_badge} {ears_text}")
            lines.append("")

        return "\n".join(lines)

    def _convert_to_ears(self, req: ParsedRequirement) -> str:
        """Convert a requirement to EARS format."""
        text = req.text
        text_lower = text.lower()

        # Determine best EARS pattern
        if any(kw in text_lower for kw in ["when", "upon", "after", "before"]):
            # Event-driven
            return f"WHEN triggered, the system SHALL {text}"
        elif any(kw in text_lower for kw in ["if", "in case", "should"]):
            # Unwanted/conditional
            return f"IF condition occurs, THEN the system SHALL {text}"
        elif any(kw in text_lower for kw in ["while", "during", "as long as"]):
            # State-driven
            return f"WHILE active, the system SHALL {text}"
        elif any(kw in text_lower for kw in ["where", "optional", "if enabled"]):
            # Optional
            return f"WHERE feature is enabled, the system SHALL {text}"
        else:
            # Ubiquitous (default)
            return f"The system SHALL {text}"

    def _generate_architecture(self, parsed: ParsedDescription) -> str:
        """Generate ASCII architecture diagram."""
        components = parsed.components or ["Frontend", "Backend", "Database"]

        # Ensure we have at least 3 components for the diagram
        while len(components) < 3:
            components.append(f"Component{len(components)+1}")

        # Create component boxes
        comp_a = components[0][:12].center(12)
        comp_b = components[1][:12].center(12) if len(components) > 1 else "Backend".center(12)
        comp_c = components[2][:12].center(12) if len(components) > 2 else "Database".center(12)

        diagram = f"""```
┌─────────────────────────────────────────────────────────────┐
│                    {parsed.hackathon_id.upper()} SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │{comp_a}│─▶│{comp_b}│─▶│{comp_c}│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Components:**
"""
        # Add component descriptions
        for i, comp in enumerate(components[:5], 1):
            diagram += f"- **{comp.title()}**: Component {i} of the system\n"

        return diagram

    def _generate_implementation_plan(self, parsed: ParsedDescription) -> str:
        """Generate implementation plan."""
        phases = []

        # Phase 1: Setup
        phases.append("""### Phase 1: Project Setup

**Tasks:**
- [ ] Initialize project structure
- [ ] Set up development environment
- [ ] Configure dependencies
- [ ] Create base configuration files

**Validation:** All setup tasks verified""")

        # Phase 2: Core Implementation
        req_tasks = "\n".join([
            f"- [ ] Implement {req.id}: {req.text[:50]}..."
            for req in parsed.requirements[:5]
        ])

        phases.append(f"""### Phase 2: Core Implementation

**Tasks:**
{req_tasks}

**Validation:** Unit tests pass for each requirement""")

        # Phase 3: Integration
        phases.append("""### Phase 3: Integration & Testing

**Tasks:**
- [ ] Integrate all components
- [ ] Write integration tests
- [ ] Perform end-to-end testing
- [ ] Document API endpoints

**Validation:** All integration tests pass""")

        # Phase 4: Deployment
        phases.append("""### Phase 4: Deployment

**Tasks:**
- [ ] Configure deployment platform
- [ ] Set up CI/CD pipeline
- [ ] Deploy to staging
- [ ] Verify production deployment

**Validation:** Application accessible and functional""")

        return "\n\n".join(phases)

    def _generate_validation_criteria(self, parsed: ParsedDescription) -> str:
        """Generate validation criteria."""
        criteria = ["### Acceptance Criteria\n"]

        for req in parsed.requirements[:10]:
            criteria.append(f"- [ ] {req.id} validated: {req.text[:60]}...")

        criteria.append("\n### Quality Checks\n")
        criteria.append("- [ ] All unit tests pass")
        criteria.append("- [ ] Code coverage > 80%")
        criteria.append("- [ ] No critical security vulnerabilities")
        criteria.append("- [ ] Documentation complete")

        return "\n".join(criteria)

    def _format_dependencies(self, technologies: list[str]) -> str:
        """Format technology dependencies."""
        if not technologies:
            return "*Dependencies to be determined based on implementation.*"

        deps = ["### Technologies\n"]
        for tech in technologies:
            deps.append(f"- {tech}")

        deps.append("\n### Package Dependencies\n")
        deps.append("*Specific versions to be determined during implementation.*")

        return "\n".join(deps)

    def _estimate_effort(self, parsed: ParsedDescription) -> str:
        """Estimate implementation effort."""
        req_count = len(parsed.requirements)

        if req_count <= 5:
            return "2-4 hours"
        elif req_count <= 10:
            return "4-8 hours"
        elif req_count <= 20:
            return "1-2 days"
        else:
            return "2-5 days"
