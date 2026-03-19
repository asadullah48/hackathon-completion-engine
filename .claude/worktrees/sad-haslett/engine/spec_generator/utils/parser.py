"""
Description Parser - Extract requirements from hackathon descriptions.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedRequirement:
    """A parsed requirement from the description."""

    id: str
    text: str
    category: str  # functional, non_functional, constraint
    priority: str = "medium"  # critical, high, medium, low
    keywords: list[str] = field(default_factory=list)


@dataclass
class ParsedDescription:
    """Complete parsed hackathon description."""

    hackathon_id: str
    title: str
    summary: str
    requirements: list[ParsedRequirement]
    components: list[str]
    technologies: list[str]
    constraints: list[str]


class DescriptionParser:
    """Parse hackathon descriptions into structured requirements."""

    # Patterns for identifying requirement types
    FUNCTIONAL_PATTERNS = [
        r"(?:shall|must|will|should)\s+(?:be able to|provide|support|allow|enable)",
        r"(?:user|system|app)\s+(?:can|should|must)\s+",
        r"(?:feature|functionality):\s*",
        r"(?:implement|create|build|develop)\s+",
    ]

    NON_FUNCTIONAL_PATTERNS = [
        r"(?:performance|speed|latency|throughput)\s*[:<]",
        r"(?:security|encryption|authentication)\s+",
        r"(?:scalability|availability|reliability)\s+",
        r"(?:maintainability|testability|usability)\s+",
        r"(?:must complete|within|less than)\s+\d+",
    ]

    PRIORITY_KEYWORDS = {
        "critical": ["critical", "essential", "must have", "required", "mandatory"],
        "high": ["important", "high priority", "should have", "key"],
        "medium": ["medium", "nice to have", "desired"],
        "low": ["optional", "low priority", "could have", "future"],
    }

    TECHNOLOGY_PATTERNS = [
        r"\b(python|typescript|javascript|rust|go|java)\b",
        r"\b(react|nextjs|fastapi|django|flask|express)\b",
        r"\b(postgresql|mongodb|redis|sqlite)\b",
        r"\b(docker|kubernetes|railway|vercel)\b",
        r"\b(api|rest|graphql|grpc)\b",
    ]

    def __init__(self):
        self._req_counter = 0

    def parse(self, hackathon_id: str, description: str) -> ParsedDescription:
        """Parse a hackathon description into structured format."""
        self._req_counter = 0

        # Extract title from first line or heading
        title = self._extract_title(description)

        # Extract summary (first paragraph after title)
        summary = self._extract_summary(description)

        # Parse requirements
        requirements = self._extract_requirements(hackathon_id, description)

        # Extract components
        components = self._extract_components(description)

        # Extract technologies
        technologies = self._extract_technologies(description)

        # Extract constraints
        constraints = self._extract_constraints(description)

        return ParsedDescription(
            hackathon_id=hackathon_id,
            title=title,
            summary=summary,
            requirements=requirements,
            components=components,
            technologies=technologies,
            constraints=constraints,
        )

    def _extract_title(self, description: str) -> str:
        """Extract title from description."""
        lines = description.strip().split("\n")
        for line in lines:
            line = line.strip()
            # Check for markdown heading
            if line.startswith("#"):
                return line.lstrip("#").strip()
            # First non-empty line as fallback
            if line:
                return line[:100]  # Limit length
        return "Untitled Hackathon"

    def _extract_summary(self, description: str) -> str:
        """Extract summary paragraph."""
        paragraphs = re.split(r"\n\s*\n", description)
        for para in paragraphs[1:3]:  # Skip title, check next 2
            para = para.strip()
            if len(para) > 50 and not para.startswith("#"):
                return para[:500]  # Limit length
        return paragraphs[0][:500] if paragraphs else ""

    def _extract_requirements(
        self, hackathon_id: str, description: str
    ) -> list[ParsedRequirement]:
        """Extract requirements from description."""
        requirements = []

        # Split into sentences/lines
        sentences = re.split(r"[.\n]", description)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            # Determine category
            category = self._categorize_requirement(sentence)
            if category:
                self._req_counter += 1
                req_id = f"{hackathon_id.upper()}-REQ-{self._req_counter:03d}"

                requirements.append(ParsedRequirement(
                    id=req_id,
                    text=sentence,
                    category=category,
                    priority=self._determine_priority(sentence),
                    keywords=self._extract_keywords(sentence),
                ))

        return requirements

    def _categorize_requirement(self, text: str) -> Optional[str]:
        """Categorize a requirement based on patterns."""
        text_lower = text.lower()

        # Check for non-functional first (more specific)
        for pattern in self.NON_FUNCTIONAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "non_functional"

        # Check for functional
        for pattern in self.FUNCTIONAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "functional"

        # Check for constraint keywords
        constraint_keywords = ["constraint", "limitation", "restriction", "boundary"]
        if any(kw in text_lower for kw in constraint_keywords):
            return "constraint"

        return None

    def _determine_priority(self, text: str) -> str:
        """Determine requirement priority from text."""
        text_lower = text.lower()

        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return priority

        return "medium"

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract relevant keywords from text."""
        keywords = []
        text_lower = text.lower()

        # Technical keywords
        tech_keywords = [
            "api", "database", "authentication", "deploy", "test",
            "frontend", "backend", "ui", "ux", "performance", "security",
            "integration", "automation", "monitoring", "logging"
        ]

        for kw in tech_keywords:
            if kw in text_lower:
                keywords.append(kw)

        return keywords

    def _extract_components(self, description: str) -> list[str]:
        """Extract system components from description."""
        components = []
        text_lower = description.lower()

        component_patterns = [
            r"(?:component|module|service|layer):\s*(\w+)",
            r"(\w+)\s+(?:component|module|service|layer)",
        ]

        for pattern in component_patterns:
            matches = re.findall(pattern, text_lower)
            components.extend(matches)

        # Common component names
        common_components = [
            "frontend", "backend", "api", "database", "auth",
            "notification", "scheduler", "worker", "cache"
        ]

        for comp in common_components:
            if comp in text_lower and comp not in components:
                components.append(comp)

        return list(set(components))

    def _extract_technologies(self, description: str) -> list[str]:
        """Extract technology stack from description."""
        technologies = []

        for pattern in self.TECHNOLOGY_PATTERNS:
            matches = re.findall(pattern, description, re.IGNORECASE)
            technologies.extend([m.lower() for m in matches])

        return list(set(technologies))

    def _extract_constraints(self, description: str) -> list[str]:
        """Extract project constraints."""
        constraints = []

        # Time constraints
        time_matches = re.findall(
            r"(?:within|in|under|less than)\s+(\d+\s*(?:hour|day|week|minute)s?)",
            description,
            re.IGNORECASE
        )
        constraints.extend([f"Time: {m}" for m in time_matches])

        # Token/cost constraints
        token_matches = re.findall(
            r"(\d+[kK]?\s*tokens?)",
            description
        )
        constraints.extend([f"Token budget: {m}" for m in token_matches])

        return constraints
