from dataclasses import dataclass

from .base import BaseRequest


class GetEndpointRequest(BaseRequest):
    endpoint: str


@dataclass
class GetEndpointClientsRequest(BaseRequest):
    endpoint: str
