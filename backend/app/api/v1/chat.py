from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.ai.orchestrator import AIInterpretationOrchestrator
from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.models.entities import Conversation, Message
from backend.app.repositories.scoped import ChartRepository, ConversationRepository

router = APIRouter(prefix="/conversations", tags=["Conversations & Multi-Turn Chat"])


class ConversationCreate(BaseModel):
    title: str = Field("Vedic Chart Consultation", min_length=1, max_length=100)
    chart_id: str | None = Field(None, description="Optional natal chart ID to attach to consultation")


class ConversationOut(BaseModel):
    id: str
    owner_id: str
    chart_id: str | None
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=2, max_length=1000)


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    content: str
    citations: list[dict[str, Any]] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatExchangeResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    citations: list[dict[str, Any]]
    tools_called: list[str]
    disclaimer: str


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a new conversation session, optionally bound to an authorized natal chart."""
    if payload.chart_id:
        chart_repo = ChartRepository(db)
        chart = chart_repo.get_by_id(payload.chart_id, owner_id=current_user.user_id)
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chart '{payload.chart_id}' not found or access denied.",
            )

    conv_repo = ConversationRepository(db)
    conv = conv_repo.create(
        owner_id=current_user.user_id,
        title=payload.title,
        chart_id=payload.chart_id,
    )
    return conv


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists all conversations owned by the authenticated user."""
    return (
        db.query(Conversation)
        .filter(Conversation.owner_id == current_user.user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves a specific conversation with strict owner authorization."""
    conv_repo = ConversationRepository(db)
    conv = conv_repo.get_by_id(conversation_id, owner_id=current_user.user_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )
    return conv


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists all messages in a conversation strictly scoped to the owner."""
    conv_repo = ConversationRepository(db)
    conv = conv_repo.get_by_id(conversation_id, owner_id=current_user.user_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.owner_id == current_user.user_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.post("/{conversation_id}/messages", response_model=ChatExchangeResponse)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sends a user message, runs the AI orchestrator against the attached chart,
    and records both user and assistant messages with citations and tool audit records.
    """
    conv_repo = ConversationRepository(db)
    conv = conv_repo.get_by_id(conversation_id, owner_id=current_user.user_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )

    # 1. Record User Message
    user_msg = Message(
        conversation_id=conversation_id,
        owner_id=current_user.user_id,
        sender_type="user",
        content=payload.content,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 2. Execute AI Orchestrator if chart is attached
    citations: list[dict[str, Any]] = []
    tools_called: list[str] = []
    disclaimer = ""
    assistant_content = ""

    if conv.chart_id:
        orchestrator = AIInterpretationOrchestrator(db=db, user_context=current_user)
        try:
            interp_res = orchestrator.interpret(chart_id=str(conv.chart_id), question=payload.content)
            assistant_content = interp_res.interpretation
            citations = [dict(c) for c in interp_res.citations]
            tools_called = interp_res.tools_called
            disclaimer = interp_res.disclaimer
        except Exception as e:
            assistant_content = f"An error occurred while evaluating chart consultation: {str(e)}"
    else:
        assistant_content = (
            "No natal chart is attached to this conversation. Please link a birth chart to enable "
            "deterministic Parashari rule evaluations and classical citations."
        )

    # 3. Record Assistant Message
    assistant_msg = Message(
        conversation_id=conversation_id,
        owner_id=current_user.user_id,
        sender_type="assistant",
        content=assistant_content,
        citations=citations,
        tool_run_ids=tools_called,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatExchangeResponse(
        user_message=MessageOut.model_validate(user_msg),
        assistant_message=MessageOut.model_validate(assistant_msg),
        citations=citations,
        tools_called=tools_called,
        disclaimer=disclaimer,
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a conversation and its messages with owner verification."""
    conv_repo = ConversationRepository(db)
    deleted = conv_repo.delete(conversation_id, owner_id=current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )
    return None
