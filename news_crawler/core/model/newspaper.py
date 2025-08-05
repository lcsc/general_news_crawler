from pydantic import BaseModel, ConfigDict
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List, Dict
from .engine import NewsPaperEngine
from datetime import datetime
from enum import Enum

from ...common.consts import BfStatus_PENDING, BfStatus_OK

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


class NewsPaperBackFill(BaseModel ):
    status:str=BfStatus_PENDING
    msg:Optional[str]=None
    

class BackFillBase():
    backfill:Optional[Dict[str,Dict[str,NewsPaperBackFill]]]=None
    
    def addBfStatus(self,year:int,month:int,status:str, msg:str=None):
        year = str(year)
        month=str(month)
        if self.backfill is None: self.backfill={}
        if year not in self.backfill: self.backfill[year]={}
        if month not in self.backfill[year]:
            self.backfill[year][month]=NewsPaperBackFill(status=status,msg=msg)
        else:
            self.backfill[year][month].status = status
            self.backfill[year][month].msg = msg
    
    def isBfDone(self,year:int,month:int):
        year = str(year)
        month=str(month)
        if self.backfill is None: return False
        if year not in self.backfill: return False
        if month not in self.backfill[year]: return False
        return self.backfill[year][month].status == BfStatus_OK

class NewsPaper(BaseModel, BackFillBase):
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

    first_article:Optional[datetime]=None
    first_month:Optional[str]=None
    n_articulos:Optional[int]=None
    last_check:Optional[datetime]=None

    class Config:
        # Configuración para manejar la conversión con MongoDB
        arbitrary_types_allowed = True
        use_enum_values = True

    

class NewsPaperRepository(AbstractRepository[NewsPaper]):
    class Meta:
        collection_name = 'NewsPapers'

class NewsArticle(BaseModel):
    id: Optional[PydanticObjectId] = None
    np_name: str
    np_ccaa: str
    np_provincia: Optional[str] = None
    article_id:str
    article_url:str
    article_headline:str
    date:datetime
    engine_id:str
    engine_data:Optional[any]=None
    raw_data:Optional[str]=None
    article_data:Optional[str]=None
    categories:Optional[List[str]]=None
    is_headline_drought:Optional[bool]=None
    
    class Config:
        # Configuración para manejar la conversión con MongoDB
        arbitrary_types_allowed = True
        use_enum_values = True

class NewsArticleRepository(AbstractRepository[NewsArticle]):
    class Meta:
        collection_name = 'NewsArticles'
