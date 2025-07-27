from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import AgentSession, AgentMessage, User
from app.schemas.agent import (
    AgentSession as AgentSessionSchema, 
    AgentSessionCreate, 
    AgentMessage as AgentMessageSchema,
    AgentMessageCreate
)
from app.api.endpoints.auth import get_current_user
import uuid

router = APIRouter()

@router.post("/sessions", response_model=AgentSessionSchema)
async def create_agent_session(
    session: AgentSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_id = str(uuid.uuid4())
    db_session = AgentSession(
        user_id=current_user.id,
        session_id=session_id,
        agent_type=session.agent_type,
        context=session.context
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[AgentSessionSchema])
async def read_agent_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=AgentSessionSchema)
async def read_agent_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    return session

@router.post("/sessions/{session_id}/messages", response_model=AgentMessageSchema)
async def create_agent_message(
    session_id: str,
    message: AgentMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session exists and belongs to user
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    
    message.session_id = session_id
    db_message = AgentMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/sessions/{session_id}/messages", response_model=List[AgentMessageSchema])
async def read_agent_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session exists and belongs to user
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    
    messages = db.query(AgentMessage).filter(
        AgentMessage.session_id == session_id
    ).offset(skip).limit(limit).all()
    return messages