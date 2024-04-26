from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    pass


class BaseRequest(BaseModel):
    pass
