from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List, Dict
from datetime import datetime
from ...core.model.newspaper import NewsPaperBackFill
from ...common.consts import BfStatus_OK

class BcubeCategory(BaseModel):
    id: Optional[PydanticObjectId] = None
    ccaa:str
    short_name:str
    cat_name:str
    cat_url:str
    first_article:Optional[datetime]=None
    first_month:Optional[str]=None
    n_articulos:Optional[int]=None
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
    
    def isCatDone(self,year:int,month:int):
        year = str(year)
        month=str(month)
        if self.backfill is None: return False
        if year not in self.backfill: return False
        if month not in self.backfill[year]: return False
        return self.backfill[year][month].status == BfStatus_OK
    
class BcubeCategoryRepository(AbstractRepository[BcubeCategory]):
    class Meta:
        collection_name = 'bCubeCategory'