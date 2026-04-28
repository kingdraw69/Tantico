from pydantic import BaseModel, Field, field_validator


class GuestLoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user_id: str
    is_guest: bool = True


class OAuthVerifyRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    id_token: str = Field(min_length=1)
    email: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, max_length=120)

    @field_validator('provider')
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        if value and '@' not in value:
            raise ValueError('El correo debe tener un formato válido.')
        return value or None

    @field_validator('display_name')
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class OAuthVerifyResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user_id: str
    is_guest: bool = False
    provider: str
