from .base import BaseRequest


class AuthRequest(BaseRequest):
    email: str
    password: str
