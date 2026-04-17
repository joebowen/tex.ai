from typing import List, Literal
from pydantic import BaseModel


class LatexRequest(BaseModel):
    message: str


class LatexResponse(BaseModel):
    intent: Literal["generate", "fix", "explain", "convert"]
    latex: str
    display_mode: Literal["inline", "block"]
    explanation: str
    warnings: List[str]