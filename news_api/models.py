from pydantic import BaseModel
from enum import Enum
from typing import List,Dict,Optional,Generic,TypeVar
from datetime import datetime
from news_crawler.core.model import NewsArticle, NewsPaper

class PagedResult():    
    results:int=0
    pages:int=0

    
class SortTypeEnum(str, Enum):
    asc = "asc"
    desc = "desc"

class PaginationParams():
    page:Optional[int]=1
    rowsPerPage:Optional[int]=25
    sortBy: Optional[str | List[str]]=None
    sortType: Optional[SortTypeEnum | List[SortTypeEnum]]=None

class BaseRequest():
    engine:Optional[str]=None
    sub_engine:Optional[str]=None

class NewsPaperSearch(BaseModel,BaseRequest,PaginationParams):
    pass

class NewsPaperResult(BaseModel,PagedResult):
    items:List[NewsPaper]=[]

class OptionsResult(BaseModel):
    ccaas:List[str]=None
    provincias:Dict[str,List[str]]=None
    engines:List[str]=None
    sub_engines:List[str]=None


class NewsSearch(BaseModel, PaginationParams):
    notBefore:Optional[datetime]=None
    notAfter:Optional[datetime]=None
    category:Optional[List[str]]=None

class NewsSearchResult(BaseModel,PagedResult):
    items:List[NewsArticle]=[]