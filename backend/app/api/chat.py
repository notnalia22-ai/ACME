import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db.connection import get_session
from app.assistant.client import GroqClient

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    tool_calls_used: list[str]
    duration_ms: int


def get_db_session():
    return get_session()


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db_session=Depends(get_db_session),
):
    start_ms = int(time.time() * 1000)

    # Put your actual groq key here
    client = GroqClient(
        api_key="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")

    try:
        answer, tool_calls_used = client.chat(request.question, db_session)
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    duration_ms = int(time.time() * 1000) - start_ms
    return ChatResponse(
        answer=answer,
        tool_calls_used=tool_calls_used,
        duration_ms=duration_ms,
    )
