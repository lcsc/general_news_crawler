from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List

class NewsPaperListerInfo(BaseModel):
    ccaa: str
    provincia: Optional[str] = None
    name: str
    type: Optional[str] = None
    url: str
    src: str
    city: Optional[str] = None

class NewsPaper(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    ccaa: str
    provincia: Optional[str] = None
    short_name:str
    real_url: Optional[str]
    alt_urls:Optional[List[str]]=None
    lister_info: Optional[List[NewsPaperListerInfo]] = None
    class Config:
        # Configuración para manejar la conversión con MongoDB
        arbitrary_types_allowed = True


    

class NewsPaperRepository(AbstractRepository[NewsPaper]):
    class Meta:
        collection_name = 'NewsPapers'