from .option import Option
from homeassistant.backports.enum import StrEnum

from .base import BaseRequest


class Mode(StrEnum):
    AUTO = "auto"
    MANUAL = "manual"
    SCHEDULE = "schedule"
    NODE_ON = "nodeOn"
    NODE_OFF = "nodeOff"
    STATION = "station"
    TURBO = "turbo"
    VENTILATION = "ventilation"
    OFF = "off"


class SetModeRequest(BaseRequest):
    endpoint: str
    mode: Mode
    option: Option
