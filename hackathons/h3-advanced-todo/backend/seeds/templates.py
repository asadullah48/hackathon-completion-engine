"""Seed data for built-in templates."""
from sqlalchemy.orm import Session
from models import Template

BUILTIN_TEMPLATES = [
    {
        "name": "Project Kickoff",
        "description": "Standard steps to start a new project successfully",
        "category": "work",
        "tags": ["work", "project", "planning"],
        "todos": [
            {
                "title": "Define project scope and objectives",
                "description": "Document the goals, deliverables, and success criteria",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": 1
            },
            {
                "title": "Create project timeline and milestones",
                "description": "Break down the project into phases with deadlines",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": 2
            },
            {
                "title": "Assign team roles and responsibilities",
                "description": "Define who is responsible for each aspect of the project",
                "category": "work",
                "priority": "medium",
                "relative_deadline_days": 3
            },
            {
                "title": "Set up development environment and repository",
                "description": "Initialize version control, CI/CD, and development tools",
                "category": "work",
                "priority": "medium",
                "relative_deadline_days": 3
            },
            {
                "title": "Schedule kickoff meeting with stakeholders",
                "description": "Align all team members and stakeholders on project goals",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": 5
            }
        ]
    },
    {
        "name": "Weekly Exercise Routine",
        "description": "Balanced weekly fitness plan for staying healthy",
        "category": "health",
        "tags": ["health", "fitness", "routine", "weekly"],
        "todos": [
            {
                "title": "Monday: Cardio - 30 minute run or walk",
                "description": "Start the week with cardiovascular exercise",
                "category": "health",
                "priority": "medium",
                "relative_deadline_days": 1
            },
            {
                "title": "Wednesday: Strength training - Upper body",
                "description": "Focus on arms, chest, and back exercises",
                "category": "health",
                "priority": "medium",
                "relative_deadline_days": 3
            },
            {
                "title": "Friday: Cardio - Cycling or swimming 45 min",
                "description": "End the work week with endurance training",
                "category": "health",
                "priority": "medium",
                "relative_deadline_days": 5
            },
            {
                "title": "Saturday: Yoga and stretching session",
                "description": "Recovery day with flexibility exercises",
                "category": "health",
                "priority": "low",
                "relative_deadline_days": 6
            }
        ]
    },
    {
        "name": "Exam Preparation",
        "description": "Systematic approach to study for important exams",
        "category": "study",
        "tags": ["study", "exam", "learning", "academic"],
        "todos": [
            {
                "title": "Review all lecture notes and materials",
                "description": "Go through course content systematically",
                "category": "study",
                "priority": "high",
                "relative_deadline_days": 7
            },
            {
                "title": "Create summary sheets for each chapter",
                "description": "Condense key concepts into review sheets",
                "category": "study",
                "priority": "high",
                "relative_deadline_days": 5
            },
            {
                "title": "Practice problems from textbook",
                "description": "Work through exercises to test understanding",
                "category": "study",
                "priority": "high",
                "relative_deadline_days": 3
            },
            {
                "title": "Review past exams and sample questions",
                "description": "Familiarize with exam format and question types",
                "category": "study",
                "priority": "medium",
                "relative_deadline_days": 2
            },
            {
                "title": "Get good night sleep before exam",
                "description": "Rest is crucial for memory and performance",
                "category": "health",
                "priority": "high",
                "relative_deadline_days": 1
            }
        ]
    },
    {
        "name": "Code Review Checklist",
        "description": "Thorough code review process for quality assurance",
        "category": "work",
        "tags": ["work", "coding", "review", "development"],
        "todos": [
            {
                "title": "Read PR description and requirements",
                "description": "Understand what the code changes aim to achieve",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": None
            },
            {
                "title": "Check code formatting and style",
                "description": "Ensure consistency with project conventions",
                "category": "work",
                "priority": "medium",
                "relative_deadline_days": None
            },
            {
                "title": "Review logic and algorithm correctness",
                "description": "Verify the implementation solves the problem correctly",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": None
            },
            {
                "title": "Verify test coverage and passing tests",
                "description": "Check that tests are comprehensive and passing",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": None
            },
            {
                "title": "Check for security vulnerabilities",
                "description": "Look for common security issues and risks",
                "category": "work",
                "priority": "high",
                "relative_deadline_days": None
            },
            {
                "title": "Leave constructive feedback and approve",
                "description": "Provide helpful comments and complete the review",
                "category": "work",
                "priority": "medium",
                "relative_deadline_days": None
            }
        ]
    },
    {
        "name": "Daily Morning Routine",
        "description": "Productive way to start your day",
        "category": "personal",
        "tags": ["personal", "routine", "morning", "productivity"],
        "todos": [
            {
                "title": "Wake up and hydrate - drink water",
                "description": "Start the day by rehydrating your body",
                "category": "health",
                "priority": "high",
                "relative_deadline_days": None
            },
            {
                "title": "Morning exercise or stretching (15 min)",
                "description": "Get the blood flowing with light exercise",
                "category": "health",
                "priority": "medium",
                "relative_deadline_days": None
            },
            {
                "title": "Prepare and eat healthy breakfast",
                "description": "Fuel your body for the day ahead",
                "category": "health",
                "priority": "high",
                "relative_deadline_days": None
            },
            {
                "title": "Review daily goals and priorities",
                "description": "Plan your day and set clear objectives",
                "category": "personal",
                "priority": "medium",
                "relative_deadline_days": None
            },
            {
                "title": "Check and respond to urgent messages",
                "description": "Clear important communications early",
                "category": "work",
                "priority": "low",
                "relative_deadline_days": None
            }
        ]
    }
]


def seed_templates(db: Session) -> int:
    """
    Seed database with built-in templates.

    Args:
        db: Database session

    Returns:
        Number of templates seeded
    """
    seeded = 0

    for template_data in BUILTIN_TEMPLATES:
        # Check if template already exists
        existing = db.query(Template).filter(
            Template.name == template_data['name'],
            Template.created_by == "system"
        ).first()

        if existing:
            continue

        template = Template(
            name=template_data['name'],
            description=template_data['description'],
            category=template_data.get('category'),
            todos=template_data['todos'],
            tags=template_data.get('tags', []),
            is_public=True,
            created_by="system"
        )

        db.add(template)
        seeded += 1

    if seeded > 0:
        db.commit()
        print(f"✅ Seeded {seeded} templates")

    return seeded
