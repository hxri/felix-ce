from pydantic import BaseModel


class PersonAttributes(BaseModel):
    height_cm: float | None = None
    weight_kg: float | None = None
    gender: str | None = None
    age: int | None = None
