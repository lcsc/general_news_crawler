from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List, Dict
from .engine import NewsPaperEngine

class NewsPaperListerInfo(BaseModel):
    name: str
    ccaa: str
    provincia: Optional[str] = None
    city: Optional[str] = None
    type: Optional[str] = None
    url: str
    src: str
    
    
    def compare(self, other)->dict:
        ret = {}
        myself = self.model_dump()
        other = other.model_dump()
        for key in myself:
            if myself[key] != other[key]:
                ret[key] = other[key]
        return ret

class NewsPaper(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    ccaa: str
    provincia: Optional[str] = None
    city: Optional[str] = None
    type: Optional[str] = None

    short_name:str
    real_url: Optional[str]
    alt_urls:Optional[List[str]]=None
    lister_info: Optional[List[NewsPaperListerInfo]] = None

    engine: Optional[NewsPaperEngine] = None
    url_fails: Optional[Dict[str,str]] = None
    class Config:
        # Configuración para manejar la conversión con MongoDB
        arbitrary_types_allowed = True


    

class NewsPaperRepository(AbstractRepository[NewsPaper]):
    class Meta:
        collection_name = 'NewsPapers'