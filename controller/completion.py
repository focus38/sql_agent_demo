from model.api import AgentRequest
from agents.db_agent import DatabaseAgent
from llm.moderator import ModeratorService
from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from app_service import get_agent, get_moderator_service


completion_router = APIRouter()

@completion_router.post("/completion")
async def get_response(
        request: AgentRequest,
        moderator_service: ModeratorService = Depends(get_moderator_service),
        agent: DatabaseAgent = Depends(get_agent)):
    if not request.question.strip():
        return JSONResponse(status_code=400, content={"detail": "Запрос пользователя должен быть указан."})

    try:
        decision, answer = await moderator_service.evaluate_user_query(request.question)
        if not decision:
            return {"moderator_decision": decision, "answer": answer}

        result = await agent.process_query_async(request.question)
        return {"moderator_decision": decision, "answer": result}
    except Exception:
        raise HTTPException(status_code=500, detail="Error generating response")
