from .base import BaseRequest


class SetDeviceSettingsRequest(BaseRequest):
    endpoint: str
    calibration: float
