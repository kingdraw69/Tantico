from pydantic import BaseModel


class PrivacyDeleteResponse(BaseModel):
    message: str
    deleted_user_id: str
