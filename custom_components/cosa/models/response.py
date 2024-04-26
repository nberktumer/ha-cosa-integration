from typing import Optional

from .base import BaseModel


class BaseResponse(BaseModel):
    ok: int
    code: Optional[int]
