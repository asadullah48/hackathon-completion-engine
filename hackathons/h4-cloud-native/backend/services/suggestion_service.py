"""AI Suggestion Service for generating intelligent todo recommendations."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
import random

from models.suggestion import Suggestion, SuggestionType, SuggestionStatus
from models.todo import Todo, TodoPriority, TodoStatus


class SuggestionService:
    """Service for generating and managing AI suggestions."""

    @staticmethod
    def generate_suggestions_for_todo(db: Session, todo: Todo, user_id: str) -> List[Suggestion]:
        """Generate AI suggestions for a specific todo."""
        suggestions = []

        # Priority suggestion
        priority_suggestion = SuggestionService._analyze_priority(db, todo, user_id)
        if priority_suggestion:
            suggestions.append(priority_suggestion)

        # Breakdown suggestion for complex todos
        if SuggestionService._is_complex_task(todo):
            breakdown = SuggestionService._suggest_breakdown(db, todo, user_id)
            if breakdown:
                suggestions.append(breakdown)

        # Recurring pattern suggestion
        recurring_suggestion = SuggestionService._suggest_recurring(db, todo, user_id)
        if recurring_suggestion:
            suggestions.append(recurring_suggestion)

        # Category suggestion
        category_suggestion = SuggestionService._suggest_category(db, todo, user_id)
        if category_suggestion:
            suggestions.append(category_suggestion)

        # Save all suggestions
        for suggestion in suggestions:
            db.add(suggestion)
        db.commit()

        return suggestions

    @staticmethod
    def generate_insights(db: Session, user_id: str) -> List[Suggestion]:
        """Generate general productivity insights for a user."""
        insights = []

        # Get user's todos
        todos = db.query(Todo).filter(Todo.owner_id == user_id).all()

        if not todos:
            return insights

        # Analyze completion patterns
        completed = [t for t in todos if t.status == TodoStatus.COMPLETED]
        pending = [t for t in todos if t.status == TodoStatus.PENDING]
        in_progress = [t for t in todos if t.status == TodoStatus.IN_PROGRESS]

        # Overdue analysis
        overdue = [t for t in pending if t.due_date and t.due_date < datetime.utcnow()]
        if overdue:
            insight = Suggestion(
                user_id=user_id,
                suggestion_type=SuggestionType.INSIGHT,
                title=f"You have {len(overdue)} overdue tasks",
                description="Consider reviewing and rescheduling or completing these tasks.",
                reasoning=f"Overdue tasks: {', '.join([t.title for t in overdue[:3]])}{'...' if len(overdue) > 3 else ''}",
                confidence="0.95",
                is_actionable=True,
                suggested_changes={"overdue_count": len(overdue)},
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.add(insight)
            insights.append(insight)

        # Productivity insight
        if len(completed) > 0 and len(todos) > 0:
            completion_rate = len(completed) / len(todos) * 100
            insight = Suggestion(
                user_id=user_id,
                suggestion_type=SuggestionType.INSIGHT,
                title=f"Your completion rate: {completion_rate:.1f}%",
                description="Keep up the momentum!" if completion_rate > 50 else "Try focusing on one task at a time.",
                reasoning=f"Completed {len(completed)} out of {len(todos)} tasks.",
                confidence="0.9",
                is_actionable=False,
                suggested_changes={"completion_rate": completion_rate},
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.add(insight)
            insights.append(insight)

        # Work in progress warning
        if len(in_progress) > 3:
            insight = Suggestion(
                user_id=user_id,
                suggestion_type=SuggestionType.INSIGHT,
                title="Too many tasks in progress",
                description=f"You have {len(in_progress)} tasks in progress. Consider completing some before starting new ones.",
                reasoning="Context switching between too many tasks can reduce productivity.",
                confidence="0.85",
                is_actionable=True,
                suggested_changes={"in_progress_count": len(in_progress)},
                expires_at=datetime.utcnow() + timedelta(days=3)
            )
            db.add(insight)
            insights.append(insight)

        db.commit()
        return insights

    @staticmethod
    def get_suggestions(
        db: Session,
        user_id: Optional[str] = None,
        todo_id: Optional[str] = None,
        status: Optional[SuggestionStatus] = None,
        suggestion_type: Optional[SuggestionType] = None
    ) -> List[Suggestion]:
        """Get suggestions with optional filters."""
        query = db.query(Suggestion)

        if user_id:
            query = query.filter(Suggestion.user_id == user_id)
        if todo_id:
            query = query.filter(Suggestion.todo_id == todo_id)
        if status:
            query = query.filter(Suggestion.status == status)
        if suggestion_type:
            query = query.filter(Suggestion.suggestion_type == suggestion_type)

        # Exclude expired suggestions
        query = query.filter(
            (Suggestion.expires_at == None) | (Suggestion.expires_at > datetime.utcnow())
        )

        return query.order_by(Suggestion.created_at.desc()).all()

    @staticmethod
    def update_suggestion_status(
        db: Session,
        suggestion_id: str,
        status: SuggestionStatus
    ) -> Optional[Suggestion]:
        """Update a suggestion's status."""
        suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
        if suggestion:
            suggestion.status = status
            suggestion.actioned_at = datetime.utcnow()
            db.commit()
            db.refresh(suggestion)
        return suggestion

    @staticmethod
    def apply_suggestion(db: Session, suggestion_id: str) -> Optional[dict]:
        """Apply a suggestion's changes to the associated todo."""
        suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
        if not suggestion or not suggestion.todo_id:
            return None

        todo = db.query(Todo).filter(Todo.id == suggestion.todo_id).first()
        if not todo:
            return None

        applied_changes = {}

        # Apply suggested changes
        if suggestion.suggested_changes:
            for key, value in suggestion.suggested_changes.items():
                if hasattr(todo, key):
                    setattr(todo, key, value)
                    applied_changes[key] = value

        # Mark suggestion as accepted
        suggestion.status = SuggestionStatus.ACCEPTED
        suggestion.actioned_at = datetime.utcnow()

        db.commit()
        return {"suggestion_id": suggestion_id, "applied_changes": applied_changes}

    # Private helper methods
    @staticmethod
    def _analyze_priority(db: Session, todo: Todo, user_id: str) -> Optional[Suggestion]:
        """Analyze and suggest priority adjustments."""
        # Simple heuristic: if task has keywords suggesting urgency
        urgent_keywords = ["urgent", "asap", "deadline", "important", "critical", "emergency"]
        title_lower = todo.title.lower()
        desc_lower = (todo.description or "").lower()

        has_urgent_keywords = any(kw in title_lower or kw in desc_lower for kw in urgent_keywords)

        if has_urgent_keywords and todo.priority != TodoPriority.HIGH:
            return Suggestion(
                todo_id=todo.id,
                user_id=user_id,
                suggestion_type=SuggestionType.PRIORITY,
                title="Consider increasing priority",
                description=f"This task contains urgency indicators. Consider setting it to high priority.",
                reasoning="Keywords like 'urgent', 'deadline', or 'important' detected in task.",
                confidence="0.75",
                is_actionable=True,
                suggested_changes={"priority": "high"},
                expires_at=datetime.utcnow() + timedelta(days=7)
            )

        # If task is old and still pending
        if todo.status == TodoStatus.PENDING and todo.created_at:
            age_days = (datetime.utcnow() - todo.created_at).days
            if age_days > 7 and todo.priority == TodoPriority.LOW:
                return Suggestion(
                    todo_id=todo.id,
                    user_id=user_id,
                    suggestion_type=SuggestionType.PRIORITY,
                    title="Review this aging task",
                    description=f"This task has been pending for {age_days} days. Consider prioritizing or archiving it.",
                    reasoning="Tasks pending for extended periods may need priority adjustment.",
                    confidence="0.7",
                    is_actionable=True,
                    suggested_changes={"priority": "medium"},
                    expires_at=datetime.utcnow() + timedelta(days=14)
                )

        return None

    @staticmethod
    def _is_complex_task(todo: Todo) -> bool:
        """Check if a task appears complex and could be broken down."""
        # Heuristics for complexity
        title_length = len(todo.title)
        desc_length = len(todo.description or "")

        # Long titles or descriptions often indicate complex tasks
        if title_length > 50 or desc_length > 200:
            return True

        # Keywords suggesting multiple steps
        complex_keywords = ["and then", "followed by", "multiple", "several", "various", "complete all"]
        text = f"{todo.title} {todo.description or ''}".lower()
        if any(kw in text for kw in complex_keywords):
            return True

        return False

    @staticmethod
    def _suggest_breakdown(db: Session, todo: Todo, user_id: str) -> Optional[Suggestion]:
        """Suggest breaking down a complex task."""
        # Simple mock breakdown based on task description
        subtasks = []

        # Generate mock subtasks
        base_subtasks = [
            {"title": f"Research requirements for: {todo.title[:30]}...", "priority": "medium"},
            {"title": f"Plan approach for: {todo.title[:30]}...", "priority": "medium"},
            {"title": f"Execute main work: {todo.title[:30]}...", "priority": "high"},
            {"title": f"Review and verify: {todo.title[:30]}...", "priority": "medium"},
        ]

        subtasks = base_subtasks[:random.randint(2, 4)]

        return Suggestion(
            todo_id=todo.id,
            user_id=user_id,
            suggestion_type=SuggestionType.BREAKDOWN,
            title="Consider breaking down this task",
            description="This task appears complex. Breaking it into smaller tasks can improve completion rate.",
            reasoning="Complex tasks are easier to complete when broken into manageable subtasks.",
            confidence="0.8",
            is_actionable=True,
            subtasks=subtasks,
            suggested_changes={},
            expires_at=datetime.utcnow() + timedelta(days=14)
        )

    @staticmethod
    def _suggest_recurring(db: Session, todo: Todo, user_id: str) -> Optional[Suggestion]:
        """Suggest making a task recurring."""
        recurring_keywords = ["weekly", "daily", "monthly", "every", "regular", "routine", "always"]
        text = f"{todo.title} {todo.description or ''}".lower()

        if any(kw in text for kw in recurring_keywords):
            return Suggestion(
                todo_id=todo.id,
                user_id=user_id,
                suggestion_type=SuggestionType.RECURRING,
                title="Make this a recurring task?",
                description="This task appears to be recurring in nature. Set up a recurring pattern.",
                reasoning="Keywords suggesting repetitive activity detected.",
                confidence="0.7",
                is_actionable=True,
                suggested_changes={"is_recurring": True},
                expires_at=datetime.utcnow() + timedelta(days=7)
            )

        return None

    @staticmethod
    def _suggest_category(db: Session, todo: Todo, user_id: str) -> Optional[Suggestion]:
        """Suggest a category for uncategorized or miscategorized todos."""
        category_keywords = {
            "work": ["meeting", "project", "deadline", "client", "report", "presentation"],
            "personal": ["home", "family", "personal", "self", "health", "exercise"],
            "shopping": ["buy", "purchase", "order", "shop", "get", "pick up"],
            "health": ["doctor", "appointment", "medicine", "gym", "workout", "health"],
        }

        text = f"{todo.title} {todo.description or ''}".lower()
        current_category = todo.category.value if todo.category else "other"

        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                if current_category != category:
                    return Suggestion(
                        todo_id=todo.id,
                        user_id=user_id,
                        suggestion_type=SuggestionType.CATEGORY,
                        title=f"Categorize as '{category}'?",
                        description=f"Based on the content, this task might fit better in the '{category}' category.",
                        reasoning=f"Keywords related to {category} detected in task.",
                        confidence="0.65",
                        is_actionable=True,
                        suggested_changes={"category": category},
                        expires_at=datetime.utcnow() + timedelta(days=14)
                    )

        return None


def get_suggestion_service() -> SuggestionService:
    """Factory function to get SuggestionService instance."""
    return SuggestionService()
