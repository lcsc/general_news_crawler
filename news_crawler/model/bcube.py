from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List


class BcubePiMd(BaseModel):
    id: Optional[PydanticObjectId] = None
    ccaa:str
    short_name:str
    link_on_foot:Optional[bool]
    url_head_link:Optional[str]
    url_head_og:Optional[str]
    found_cats:List[str]
    
class BcubePiMDRepository(AbstractRepository[BcubePiMd]):
    class Meta:
        collection_name = 'bCubePIMetaData'


class PrensaIbericaStat(BaseModel):
    id: Optional[PydanticObjectId] = None
    ccaa:Optional[str] = None
    short_name:str 
    js_name:Optional[str] = None
    repo_found:bool
    num_cats:int

class PrensaIbericaStatRepository(AbstractRepository[PrensaIbericaStat]):
    class Meta:
        collection_name = 'piStats'