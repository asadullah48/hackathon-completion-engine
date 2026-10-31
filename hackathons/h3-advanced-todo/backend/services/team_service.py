"""
Team service for managing teams and memberships.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from models import Team, TeamMember, User, MemberRole, Todo, TeamTodo


class TeamService:
    """Service class for team operations."""

    # Role hierarchy for permission checks
    ROLE_HIERARCHY = {
        MemberRole.OWNER: 4,
        MemberRole.ADMIN: 3,
        MemberRole.EDITOR: 2,
        MemberRole.VIEWER: 1
    }

    @staticmethod
    def create_team(
        db: Session,
        name: str,
        owner_id: str,
        description: Optional[str] = None
    ) -> Team:
        """Create a new team and add owner as member."""
        team = Team(
            name=name,
            owner_id=owner_id,
            description=description
        )
        db.add(team)
        db.flush()

        # Add owner as member with OWNER role
        member = TeamMember(
            team_id=team.id,
            user_id=owner_id,
            role=MemberRole.OWNER
        )
        db.add(member)
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def add_member(
        db: Session,
        team_id: str,
        user_id: str,
        role: MemberRole,
        added_by: str
    ) -> TeamMember:
        """Add a member to a team."""
        # Check if already a member
        existing = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        if existing:
            raise ValueError("User is already a member of this team")

        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role,
            added_by=added_by
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_member(db: Session, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

        if not member:
            return False

        # Don't allow removing the owner
        if member.role == MemberRole.OWNER:
            raise ValueError("Cannot remove the team owner")

        db.delete(member)
        db.commit()
        return True

    @staticmethod
    def update_member_role(
        db: Session,
        team_id: str,
        user_id: str,
        new_role: MemberRole
    ) -> Optional[TeamMember]:
        """Update a member's role."""
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

        if not member:
            return None

        # Don't allow changing owner role
        if member.role == MemberRole.OWNER:
            raise ValueError("Cannot change the owner's role")

        # Don't allow promoting to owner
        if new_role == MemberRole.OWNER:
            raise ValueError("Cannot promote to owner role")

        member.role = new_role
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def get_team_members(db: Session, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        return db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()

    @staticmethod
    def get_member(
        db: Session,
        team_id: str,
        user_id: str
    ) -> Optional[TeamMember]:
        """Get a specific team member."""
        return db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

    @staticmethod
    def check_permission(
        db: Session,
        user_id: str,
        team_id: str,
        min_role: MemberRole
    ) -> bool:
        """Check if user has at least the specified role in the team."""
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()

        if not member:
            return False

        user_level = TeamService.ROLE_HIERARCHY.get(member.role, 0)
        required_level = TeamService.ROLE_HIERARCHY.get(min_role, 0)
        return user_level >= required_level

    @staticmethod
    def get_user_teams(db: Session, user_id: str) -> List[Team]:
        """Get all teams a user belongs to."""
        memberships = db.query(TeamMember).filter(
            TeamMember.user_id == user_id
        ).all()
        team_ids = [m.team_id for m in memberships]

        if not team_ids:
            return []

        return db.query(Team).filter(Team.id.in_(team_ids)).all()

    @staticmethod
    def get_team_todos(db: Session, team_id: str) -> List[Todo]:
        """Get all todos associated with a team."""
        return db.query(Todo).filter(Todo.team_id == team_id).all()

    @staticmethod
    def delete_team(db: Session, team_id: str, user_id: str) -> bool:
        """Delete a team (owner only)."""
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            return False

        if team.owner_id != user_id:
            raise ValueError("Only the team owner can delete the team")

        db.delete(team)
        db.commit()
        return True

    @staticmethod
    def create_team_todo(
        db: Session,
        team_id: str,
        title: str,
        description: Optional[str] = None,
        category: str = "work",
        priority: str = "medium",
        deadline=None,
        assigned_to: Optional[str] = None,
        assigned_to_name: Optional[str] = None,
        created_by: str = "",
        created_by_name: str = ""
    ) -> TeamTodo:
        """Create a team todo."""
        todo = TeamTodo(
            team_id=team_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            deadline=deadline,
            assigned_to=assigned_to,
            assigned_to_name=assigned_to_name,
            created_by=created_by,
            created_by_name=created_by_name
        )

        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo

    @staticmethod
    def get_team_todos_by_team_id(db: Session, team_id: str) -> List[TeamTodo]:
        """Get all team todos for a specific team."""
        return db.query(TeamTodo).filter(TeamTodo.team_id == team_id).all()

    @staticmethod
    def update_team_todo(
        db: Session,
        todo_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        deadline=None,
        assigned_to: Optional[str] = None,
        assigned_to_name: Optional[str] = None
    ) -> Optional[TeamTodo]:
        """Update a team todo."""
        todo = db.query(TeamTodo).filter(TeamTodo.id == todo_id).first()

        if not todo:
            return None

        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if category is not None:
            todo.category = category
        if priority is not None:
            todo.priority = priority
        if status is not None:
            todo.status = status
        if deadline is not None:
            todo.deadline = deadline
        if assigned_to is not None:
            todo.assigned_to = assigned_to
        if assigned_to_name is not None:
            todo.assigned_to_name = assigned_to_name

        db.commit()
        db.refresh(todo)
        return todo

    @staticmethod
    def delete_team_todo(db: Session, todo_id: str) -> bool:
        """Delete a team todo."""
        todo = db.query(TeamTodo).filter(TeamTodo.id == todo_id).first()

        if not todo:
            return False

        db.delete(todo)
        db.commit()
        return True
