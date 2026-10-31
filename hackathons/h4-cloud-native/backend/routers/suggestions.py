"""Suggestions router for AI-powered recommendations."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models.suggestion import Suggestion, SuggestionType, SuggestionStatus
from models.todo import Todo
from services.suggestion_service import SuggestionService

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


# Pydantic models
class SuggestionResponse(BaseModel):
    id: str
    todo_id: Optional[str]
    user_id: Optional[str]
    suggestion_type: str
    status: str
    title: str
    description: Optional[str]
    suggested_changes: dict
    confidence: float
    reasoning: Optional[str]
    subtasks: List[dict]
    is_actionable: bool
    expires_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    actioned_at: Optional[str]

    class Config:
        from_attributes = True


class UpdateSuggestionRequest(BaseModel):
    status: str


class ApplySuggestionResponse(BaseModel):
    suggestion_id: str
    applied_changes: dict


@router.get("", response_model=List[SuggestionResponse])
def get_suggestions(
    user_id: Optional[str] = Query(None),
    todo_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    suggestion_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get suggestions with optional filters."""
    # Convert string to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = SuggestionStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    type_enum = None
    if suggestion_type:
        try:
            type_enum = SuggestionType(suggestion_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid suggestion type: {suggestion_type}")

    suggestions = SuggestionService.get_suggestions(
        db=db,
        user_id=user_id,
        todo_id=todo_id,
        status=status_enum,
        suggestion_type=type_enum
    )

    return [s.to_dict() for s in suggestions]


@router.post("/generate/{todo_id}", response_model=List[SuggestionResponse])
def generate_suggestions_for_todo(
    todo_id: str,
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Generate AI suggestions for a specific todo."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    suggestions = SuggestionService.generate_suggestions_for_todo(
        db=db,
        todo=todo,
        user_id=user_id
    )

    return [s.to_dict() for s in suggestions]


@router.post("/insights/{user_id}", response_model=List[SuggestionResponse])
def generate_insights(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Generate general productivity insights for a user."""
    insights = SuggestionService.generate_insights(db=db, user_id=user_id)
    return [s.to_dict() for s in insights]


@router.put("/{suggestion_id}", response_model=SuggestionResponse)
def update_suggestion(
    suggestion_id: str,
    request: UpdateSuggestionRequest,
    db: Session = Depends(get_db)
):
    """Update a suggestion's status (accept, dismiss, etc.)."""
    try:
        status_enum = SuggestionStatus(request.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}")

    suggestion = SuggestionService.update_suggestion_status(
        db=db,
        suggestion_id=suggestion_id,
        status=status_enum
    )

    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    return suggestion.to_dict()


@router.post("/{suggestion_id}/apply", response_model=ApplySuggestionResponse)
def apply_suggestion(
    suggestion_id: str,
    db: Session = Depends(get_db)
):
    """Apply a suggestion's changes to the associated todo."""
    result = SuggestionService.apply_suggestion(db=db, suggestion_id=suggestion_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Suggestion not found or has no associated todo"
        )

    return result


@router.delete("/{suggestion_id}")
def delete_suggestion(
    suggestion_id: str,
    db: Session = Depends(get_db)
):
    """Delete a suggestion."""
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    db.delete(suggestion)
    db.commit()

    return {"message": "Suggestion deleted", "id": suggestion_id}
