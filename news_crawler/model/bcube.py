from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List


class BcubeMD(BaseModel):
    id: Optional[PydanticObjectId] = None
    ccaa:str
    short_name:str
    link_on_foot:Optional[bool]
    url_head_link:Optional[str]
    url_head_og:Optional[str]
    found_cats:List[str]
    
class BcubeMDRepository(AbstractRepository[BcubeMD]):
    class Meta:
        collection_name = 'bCubeMetaData'