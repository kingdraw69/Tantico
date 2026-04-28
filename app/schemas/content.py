from pydantic import BaseModel


class ExerciseRead(BaseModel):
    id: str
    slug: str
    title: str
    category: str
    duration_minutes: int
    description: str
    steps: str

    model_config = {'from_attributes': True}
