from pydantic import BaseModel

class BaseRequest(BaseModel):
    engine:str=None
    sub_engine:str=None
