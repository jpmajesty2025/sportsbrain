from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AgentSessionBase(BaseModel):
    agent_type: str
    context: Optional[Dict[str, Any]] = None

class AgentSessionCreate(AgentSessionBase):
    user_id: int

class AgentSession(AgentSessionBase):
    id: int
    user_id: int
    session_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AgentMessageBase(BaseModel):
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None

class AgentMessageCreate(AgentMessageBase):
    session_id: str

class AgentMessage(AgentMessageBase):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True