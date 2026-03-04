from src.schemas.common import CamelModel


class LoginRequest(CamelModel):
    email: str
    password: str


class UserResponse(CamelModel):
    id: str
    name: str
    role: str
    unit: str
    email: str
    avatar_initials: str


class LoginResponse(CamelModel):
    user: UserResponse
    token: str
