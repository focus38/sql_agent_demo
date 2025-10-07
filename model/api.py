from typing import Optional

from pydantic import BaseModel


class AgentRequest(BaseModel):
    question: str
    model_name: Optional[str]
