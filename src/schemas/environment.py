from pydantic import BaseModel


class EnvironmentAttributes(BaseModel):
    apparel_type: str
    inferred_setting: str
    visual_cues: str
