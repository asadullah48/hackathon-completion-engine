"""
Teams router for team management and membership.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import Team, TeamMember, MemberRole, User, Todo, TeamTodo, TodoComment, TeamRole
from services import TeamService

router = APIRouter(prefix="/api/teams", tags=["teams"])


# Pydantic schemas
class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: str


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    settings: dict
    created_at: str
    updated_at: Optional[str]
    members: Optional[List[dict]] = None
    member_count: int = 0

    class Config:
        from_attributes = True


class MemberAdd(BaseModel):
    user_id: str
    role: str = "viewer"


class MemberUpdate(BaseModel):
    role: str


class MemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    role: str
    added_by: Optional[str]
    joined_at: str
    user: Optional[dict] = None

    class Config:
        from_attributes = True


class TeamTodoCreateRequest(BaseModel):
    title: str
    description: str | None = None
    category: str = "work"
    priority: str = "medium"
    deadline: datetime | None = None
    assigned_to: str | None = None
    assigned_to_name: str | None = None
    created_by_name: str


class TeamTodoResponse(BaseModel):
    id: str
    team_id: str
    title: str
    description: str | None
    category: str
    priority: str
    status: str
    deadline: datetime | None
    assigned_to: str | None
    assigned_to_name: str | None
    created_by: str
    created_by_name: str
    created_at: datetime
    comment_count: int

    class Config:
        from_attributes = True


class CommentCreateRequest(BaseModel):
    content: str
    user_id: str
    user_name: str


class CommentResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=TeamResponse)
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team. Creator becomes owner."""
    # Verify owner exists
    owner = db.query(User).filter(User.id == team_data.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")

    team = TeamService.create_team(
        db=db,
        name=team_data.name,
        owner_id=team_data.owner_id,
        description=team_data.description
    )

    return {
        **team.to_dict(include_members=True),
        "member_count": len(team.members)
    }


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    user_id: Optional[str] = Query(None, description="Filter by user membership"),
    db: Session = Depends(get_db)
):
    """List teams. If user_id provided, returns only teams user belongs to."""
    if user_id:
        teams = TeamService.get_user_teams(db, user_id)
    else:
        teams = db.query(Team).all()

    return [
        {
            **t.to_dict(include_members=False),
            "member_count": len(t.members)
        }
        for t in teams
    ]


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str, db: Session = Depends(get_db)):
    """Get team details with members."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return {
        **team.to_dict(include_members=True),
        "member_count": len(team.members)
    }


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    user_id: str = Query(..., description="User making the update"),
    db: Session = Depends(get_db)
):
    """Update team (admin+ only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check permission
    if not TeamService.check_permission(db, user_id, team_id, MemberRole.ADMIN):
        raise HTTPException(status_code=403, detail="Admin permission required")

    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description

    db.commit()
    db.refresh(team)

    return {
        **team.to_dict(include_members=True),
        "member_count": len(team.members)
    }


@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    user_id: str = Query(..., description="User requesting deletion"),
    db: Session = Depends(get_db)
):
    """Delete team (owner only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    try:
        TeamService.delete_team(db, team_id, user_id)
        return {"message": "Team deleted", "team_id": team_id}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Member endpoints
@router.get("/{team_id}/members", response_model=List[MemberResponse])
async def list_members(team_id: str, db: Session = Depends(get_db)):
    """List all members of a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    members = TeamService.get_team_members(db, team_id)
    return [m.to_dict(include_user=True) for m in members]


@router.post("/{team_id}/members", response_model=MemberResponse)
async def add_member(
    team_id: str,
    member_data: MemberAdd,
    added_by: str = Query(..., description="User adding the member"),
    db: Session = Depends(get_db)
):
    """Add a member to the team (admin+ only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check permission
    if not TeamService.check_permission(db, added_by, team_id, MemberRole.ADMIN):
        raise HTTPException(status_code=403, detail="Admin permission required")

    # Verify user exists
    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate role
    try:
        role = MemberRole(member_data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Can't add someone as owner
    if role == MemberRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot add member as owner")

    try:
        member = TeamService.add_member(db, team_id, member_data.user_id, role, added_by)
        return member.to_dict(include_user=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{team_id}/members/{user_id}")
async def remove_member(
    team_id: str,
    user_id: str,
    removed_by: str = Query(..., description="User removing the member"),
    db: Session = Depends(get_db)
):
    """Remove a member from the team (admin+ only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check permission
    if not TeamService.check_permission(db, removed_by, team_id, MemberRole.ADMIN):
        raise HTTPException(status_code=403, detail="Admin permission required")

    try:
        success = TeamService.remove_member(db, team_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"message": "Member removed", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{team_id}/members/{user_id}", response_model=MemberResponse)
async def update_member_role(
    team_id: str,
    user_id: str,
    role_data: MemberUpdate,
    updated_by: str = Query(..., description="User updating the role"),
    db: Session = Depends(get_db)
):
    """Update a member's role (admin+ only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check permission
    if not TeamService.check_permission(db, updated_by, team_id, MemberRole.ADMIN):
        raise HTTPException(status_code=403, detail="Admin permission required")

    # Validate role
    try:
        new_role = MemberRole(role_data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    try:
        member = TeamService.update_member_role(db, team_id, user_id, new_role)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member.to_dict(include_user=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Team todos
@router.get("/{team_id}/todos", response_model=List[TeamTodoResponse])
async def list_team_todos(team_id: str, db: Session = Depends(get_db)):
    """List all todos associated with a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Get team todos from the TeamTodo table
    todos = db.query(TeamTodo).filter(TeamTodo.team_id == team_id).all()
    return [
        {
            **todo.to_dict(),
            "comment_count": len(todo.comments)
        }
        for todo in todos
    ]


@router.post("/{team_id}/todos", response_model=TeamTodoResponse)
async def create_team_todo(
    team_id: str,
    request: TeamTodoCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a team todo."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    todo = TeamTodo(
        team_id=team_id,
        title=request.title,
        description=request.description,
        category=request.category,
        priority=request.priority,
        deadline=request.deadline,
        assigned_to=request.assigned_to,
        assigned_to_name=request.assigned_to_name,
        created_by="user_1",  # TODO: Get from auth
        created_by_name=request.created_by_name
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return {
        **todo.to_dict(),
        "comment_count": 0
    }


@router.put("/{team_id}/todos/{todo_id}", response_model=TeamTodoResponse)
async def update_team_todo(
    team_id: str,
    todo_id: str,
    request: TeamTodoCreateRequest,
    db: Session = Depends(get_db)
):
    """Update team todo."""
    todo = db.query(TeamTodo).filter(
        TeamTodo.id == todo_id,
        TeamTodo.team_id == team_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.title = request.title
    todo.description = request.description
    todo.category = request.category
    todo.priority = request.priority
    todo.deadline = request.deadline
    todo.assigned_to = request.assigned_to
    todo.assigned_to_name = request.assigned_to_name

    db.commit()
    db.refresh(todo)

    return {
        **todo.to_dict(),
        "comment_count": len(todo.comments)
    }


@router.delete("/{team_id}/todos/{todo_id}")
async def delete_team_todo(
    team_id: str,
    todo_id: str,
    db: Session = Depends(get_db)
):
    """Delete team todo."""
    todo = db.query(TeamTodo).filter(
        TeamTodo.id == todo_id,
        TeamTodo.team_id == team_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"deleted": True, "id": todo_id}


# Comments
@router.post("/{team_id}/todos/{todo_id}/comments", response_model=CommentResponse)
async def add_comment(
    team_id: str,
    todo_id: str,
    request: CommentCreateRequest,
    db: Session = Depends(get_db)
):
    """Add comment to team todo."""
    todo = db.query(TeamTodo).filter(
        TeamTodo.id == todo_id,
        TeamTodo.team_id == team_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    comment = TodoComment(
        todo_id=todo_id,
        user_id=request.user_id,
        user_name=request.user_name,
        content=request.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get("/{team_id}/todos/{todo_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    team_id: str,
    todo_id: str,
    db: Session = Depends(get_db)
):
    """List comments on a todo."""
    comments = db.query(TodoComment).filter(TodoComment.todo_id == todo_id).all()
    return comments


@router.delete("/{team_id}/todos/{todo_id}/comments/{comment_id}")
async def delete_comment(
    team_id: str,
    todo_id: str,
    comment_id: str,
    db: Session = Depends(get_db)
):
    """Delete a comment."""
    comment = db.query(TodoComment).filter(TodoComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {"deleted": True, "id": comment_id}
