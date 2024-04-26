from .base import BaseModel


class CombiSettings(BaseModel):
    heating: bool
    pidWindowLow: float
    pidWindowHigh: float
