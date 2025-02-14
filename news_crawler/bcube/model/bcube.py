from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List
from datetime import datetime

class BcubeCategory(BaseModel):
    id: Optional[PydanticObjectId] = None
    ccaa:str
    short_name:str
    cat_name:str
    cat_url:str
    first_article:Optional[datetime]=None
    first_month:Optional[str]=None
    n_articulos:Optional[int]=None
    
class BcubeCategoryRepository(AbstractRepository[BcubeCategory]):
    class Meta:
        collection_name = 'bCubeCategory'