from pydantic import BaseModel
from datetime import datetime


class GenerationMetadata(BaseModel):
    prompt: str
    model: str
    seed: int | None = None
    latency_sec: float
    credit_cost: float | None = None
    timestamp: datetime
