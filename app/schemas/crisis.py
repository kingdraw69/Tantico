from pydantic import BaseModel


class CrisisEvaluateRequest(BaseModel):
    text: str


class CrisisEvaluateResponse(BaseModel):
    is_crisis: bool
    severity: str
    detected_keywords: list[str]
    help_resource_name: str
    help_resource_url: str
    message: str
