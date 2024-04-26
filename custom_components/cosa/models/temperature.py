from .base import BaseRequest, BaseModel


class TargetTemperatures(BaseModel):
    away: float
    custom: float
    home: float
    sleep: float


class GetTargetTemperaturesRequest(BaseRequest):
    endpoint: str


class SetTargetTemperaturesRequest(BaseRequest):
    endpoint: str
    targetTemperatures: TargetTemperatures
