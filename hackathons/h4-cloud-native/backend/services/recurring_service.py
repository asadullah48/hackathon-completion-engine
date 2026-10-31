"""Service for managing recurring todos and generating occurrences."""
import calendar
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session

from models import RecurringTodo, Todo, TodoCategory, TodoPriority, TodoStatus


class RecurringService:
    """Service for managing recurring todos and generating occurrences."""

    @staticmethod
    def calculate_next_occurrence(recurring: RecurringTodo) -> Optional[datetime]:
        """
        Calculate next occurrence date based on recurrence pattern.

        Args:
            recurring: The recurring todo configuration

        Returns:
            Next occurrence datetime or None if past end date
        """
        # Determine base date for calculation
        if recurring.last_generated:
            base_date = recurring.last_generated
        else:
            base_date = recurring.start_date or datetime.utcnow()

        next_date = None

        if recurring.pattern == "daily":
            next_date = base_date + timedelta(days=recurring.interval)

        elif recurring.pattern == "weekly":
            next_date = base_date + timedelta(weeks=recurring.interval)

            # Adjust to specific days of week if specified
            if recurring.days_of_week:
                # Find next matching day (days_of_week: 0=Mon, 1=Tue, ..., 6=Sun)
                found = False
                for _ in range(7):
                    if next_date.weekday() in recurring.days_of_week:
                        found = True
                        break
                    next_date += timedelta(days=1)

                if not found:
                    # If no matching day in the week, use original calculation
                    next_date = base_date + timedelta(weeks=recurring.interval)

        elif recurring.pattern == "monthly":
            # Calculate target month
            month = base_date.month + recurring.interval
            year = base_date.year

            while month > 12:
                month -= 12
                year += 1

            # Determine day of month
            day = recurring.day_of_month if recurring.day_of_month else base_date.day

            # Handle month-end edge cases (e.g., Jan 31 -> Feb 28)
            max_day = calendar.monthrange(year, month)[1]
            day = min(day, max_day)

            next_date = base_date.replace(year=year, month=month, day=day)

        else:  # custom - treated as every N days
            next_date = base_date + timedelta(days=recurring.interval)

        # Check if past end date
        if recurring.end_date and next_date > recurring.end_date:
            return None

        return next_date

    @staticmethod
    def generate_occurrence(
        db: Session,
        recurring: RecurringTodo
    ) -> Optional[Todo]:
        """
        Generate next todo occurrence from recurring pattern.

        Args:
            db: Database session
            recurring: The recurring todo configuration

        Returns:
            Newly created Todo or None if no more occurrences
        """
        next_date = RecurringService.calculate_next_occurrence(recurring)

        if not next_date:
            return None

        # Get template todo
        template = recurring.template_todo
        if not template:
            return None

        # Clone template todo with new deadline
        new_todo = Todo(
            id=str(uuid.uuid4()),
            title=template.title,
            description=template.description,
            category=template.category,
            priority=template.priority,
            status=TodoStatus.PENDING,
            deadline=next_date,
            constitutional_check=template.constitutional_check,
            ai_metadata={
                "generated_from": "recurring",
                "recurring_id": recurring.id,
                "occurrence_date": next_date.isoformat(),
                "generated_at": datetime.utcnow().isoformat()
            }
        )

        db.add(new_todo)

        # Update recurring record
        recurring.last_generated = datetime.utcnow()
        recurring.next_occurrence = RecurringService.calculate_next_occurrence(recurring)

        db.commit()
        db.refresh(new_todo)

        return new_todo

    @staticmethod
    def generate_due_occurrences(db: Session) -> List[Todo]:
        """
        Generate all due recurring todo occurrences.

        This method is intended to be called by a cron job or scheduler
        to automatically generate todos when their next occurrence is due.

        Args:
            db: Database session

        Returns:
            List of newly generated todos
        """
        generated = []
        now = datetime.utcnow()

        # Find all active recurring todos that need generation
        recurring_todos = db.query(RecurringTodo).filter(
            RecurringTodo.is_active == True,
            RecurringTodo.next_occurrence <= now
        ).all()

        for recurring in recurring_todos:
            todo = RecurringService.generate_occurrence(db, recurring)
            if todo:
                generated.append(todo)

        return generated

    @staticmethod
    def preview_occurrences(
        recurring: RecurringTodo,
        count: int = 5
    ) -> List[datetime]:
        """
        Preview upcoming occurrences without generating todos.

        Args:
            recurring: The recurring todo configuration
            count: Number of occurrences to preview

        Returns:
            List of upcoming occurrence datetimes
        """
        occurrences = []

        # Create a temporary copy to calculate without modifying original
        temp_last_generated = recurring.last_generated

        for _ in range(count):
            next_date = RecurringService.calculate_next_occurrence(recurring)
            if not next_date:
                break

            occurrences.append(next_date)

            # Temporarily update for next calculation
            recurring.last_generated = next_date

        # Restore original state
        recurring.last_generated = temp_last_generated

        return occurrences


def get_recurring_service() -> RecurringService:
    """Get recurring service instance."""
    return RecurringService()
