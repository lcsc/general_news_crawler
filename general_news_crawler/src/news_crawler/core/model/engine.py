from pydantic import BaseModel
from typing import Optional, List


class NewsPaperEngine(BaseModel):
    engine: str
    sub_engine: Optional[str] = None
    evidence: Optional[dict] = None
    class Config:
        arbitrary_types_allowed = True