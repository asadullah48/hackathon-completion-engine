"""
Spec Generator - Main entry point for generating specifications.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .utils.parser import DescriptionParser, ParsedDescription
from .utils.formatter import SpecFormatter


@dataclass
class SpecGenerationResult:
    """Result of spec generation."""

    spec_file: str
    requirements_count: int
    functional_count: int
    non_functional_count: int
    estimated_effort: str
    status: str
    error: Optional[str] = None


class SpecGenerator:
    """Generate formal specifications from hackathon descriptions."""

    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize with templates directory.

        Args:
            templates_dir: Path to templates directory. Defaults to built-in templates.
        """
        self.templates_dir = Path(templates_dir) if templates_dir else None
        self.parser = DescriptionParser()
        self.formatter = SpecFormatter(self.templates_dir)

    def generate_spec(
        self,
        hackathon_id: str,
        description: str,
        output_path: str,
        author: str = "Asadullah",
        version: str = "1.0.0",
    ) -> SpecGenerationResult:
        """Generate specification from hackathon description.

        Args:
            hackathon_id: Hackathon identifier (h0, h1, etc.)
            description: Hackathon description text
            output_path: Where to save the generated spec
            author: Spec author name
            version: Spec version

        Returns:
            SpecGenerationResult with generation details
        """
        try:
            # Parse the description
            parsed = self.parser.parse(hackathon_id, description)

            # Format into spec document
            spec_content = self.formatter.format_spec(parsed, author, version)

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(spec_content)

            # Count requirements by type
            functional_count = len([
                r for r in parsed.requirements if r.category == "functional"
            ])
            non_functional_count = len([
                r for r in parsed.requirements if r.category == "non_functional"
            ])

            return SpecGenerationResult(
                spec_file=str(output_file),
                requirements_count=len(parsed.requirements),
                functional_count=functional_count,
                non_functional_count=non_functional_count,
                estimated_effort=self.formatter._estimate_effort(parsed),
                status="success",
            )

        except Exception as e:
            return SpecGenerationResult(
                spec_file="",
                requirements_count=0,
                functional_count=0,
                non_functional_count=0,
                estimated_effort="unknown",
                status="error",
                error=str(e),
            )

    def parse_description(self, hackathon_id: str, description: str) -> ParsedDescription:
        """Parse description without generating file.

        Useful for previewing or further processing.

        Args:
            hackathon_id: Hackathon identifier
            description: Description text

        Returns:
            ParsedDescription object
        """
        return self.parser.parse(hackathon_id, description)

    def generate_from_file(
        self,
        hackathon_id: str,
        description_file: str,
        output_path: str,
        **kwargs,
    ) -> SpecGenerationResult:
        """Generate spec from a description file.

        Args:
            hackathon_id: Hackathon identifier
            description_file: Path to description markdown/text file
            output_path: Where to save the generated spec
            **kwargs: Additional arguments passed to generate_spec

        Returns:
            SpecGenerationResult
        """
        desc_path = Path(description_file)
        if not desc_path.exists():
            return SpecGenerationResult(
                spec_file="",
                requirements_count=0,
                functional_count=0,
                non_functional_count=0,
                estimated_effort="unknown",
                status="error",
                error=f"Description file not found: {description_file}",
            )

        description = desc_path.read_text()
        return self.generate_spec(hackathon_id, description, output_path, **kwargs)

    def validate_spec(self, spec_path: str) -> dict:
        """Validate a generated spec file.

        Args:
            spec_path: Path to spec file

        Returns:
            Validation result dictionary
        """
        path = Path(spec_path)
        if not path.exists():
            return {"valid": False, "error": "File not found"}

        content = path.read_text()

        issues = []

        # Check for required sections
        required_sections = [
            "Executive Summary",
            "Requirements",
            "System Architecture",
            "Implementation Plan",
            "Validation Criteria",
        ]

        for section in required_sections:
            if section not in content:
                issues.append(f"Missing section: {section}")

        # Check for at least one requirement
        if "REQ-" not in content:
            issues.append("No requirements found (missing REQ-XXX identifiers)")

        # Check for placeholder variables
        if "{{" in content and "}}" in content:
            issues.append("Unresolved template placeholders found")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "sections_found": [s for s in required_sections if s in content],
        }
