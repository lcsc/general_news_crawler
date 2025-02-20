from pydantic import BaseModel

from typing import List,Dict,Optional

class BaseRequest(BaseModel):
    engine:Optional[str]=None
    sub_engine:Optional[str]=None


class OptionsResult(BaseModel):
    ccaas:List[str]=None
    provincias:Dict[str,List[str]]=None
    engines:List[str]=None
    sub_engines:List[str]=None
