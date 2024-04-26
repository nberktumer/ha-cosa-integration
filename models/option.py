from homeassistant.backports.enum import StrEnum

from .base import BaseRequest


class Option(StrEnum):
    HOME = "home"
    SLEEP = "sleep"
    AWAY = "away"
    FROZEN = "frozen"
    CUSTOM = "custom"
    REMOTE = "remote"
    AUTO = "auto"
    OFF = "off"


class SetOptionRequest(BaseRequest):
    endpoint: str
    option: Option
