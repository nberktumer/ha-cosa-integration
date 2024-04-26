from .settings import CombiSettings

from .base import BaseRequest


class SetCombiSettingsRequest(BaseRequest):
    endpoint: str
    combiSettings: CombiSettings
