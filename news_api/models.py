from pydantic import BaseModel
from enum import Enum
from typing import List,Dict,Optional
from datetime import datetime
from news_crawler.core.model import NewsArticle

class BaseRequest(BaseModel):
    engine:Optional[str]=None
    sub_engine:Optional[str]=None


class OptionsResult(BaseModel):
    ccaas:List[str]=None
    provincias:Dict[str,List[str]]=None
    engines:List[str]=None
    sub_engines:List[str]=None

class SortTypeEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class PaginationParams():
    page:Optional[int]=1
    rowsPerPage:Optional[int]=25
    sortBy: Optional[str | List[str]]=None
    sortType: Optional[SortTypeEnum | List[SortTypeEnum]]=None

class NewsSearch(BaseModel, PaginationParams):
    notBefore:Optional[datetime]=None

class NewsSearchResult(BaseModel):
    results:int=0
    pages:int=0
    items:List[NewsArticle]=[]