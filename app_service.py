from app import agent, moderator_service
from agents.smol_agent import DatabaseAgent
from llm.moderator import ModeratorService


def get_agent() -> DatabaseAgent:
    return agent

def get_moderator_service() -> ModeratorService:
    return moderator_service