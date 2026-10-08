from .models import BaseRequest, SortTypeEnum
from news_crawler.core.model import CrawlerRepos
from news_crawler.common.tools import connect_mongo


import logging
from typing import Optional, List,Sequence,Tuple

LOG = logging.getLogger(__name__)


def build_query(ccaa:str=None,provincia:str=None,query:BaseRequest=None):
    ret = {}
    if ccaa is not None: ret.update({"ccaa":ccaa})
    if provincia is not None: ret.update({"provincia":provincia})
    if query is not None:
        if query.engine is not None: ret.update({"engine.engine":query.engine})
        if query.sub_engine is not None: ret.update({"engine.sub_engine":query.sub_engine})
    return ret
def serialize_document(doc):
    #doc["_id"] = str(doc["_id"])
    return doc

def getSortDirection(sortType:SortTypeEnum | List[SortTypeEnum],i:int)->int:
    if sortType is None: return 1

    if type(sortType) is list:
        sortType = sortType[i] 

    if sortType == SortTypeEnum.asc:
        return 1
    else:
        return -1

def buildSort(sortFields:Optional[str | List[str]], sortOrders:Optional[SortTypeEnum | List[SortTypeEnum]])->Sequence[Tuple[str, int]]:
    if sortFields is None or len(sortFields)==0: return None
    ret = []

    if type(sortFields) is str:
        sortFields = [sortFields]
    for i,sortField in enumerate(sortFields):
        ret.append((sortField, getSortDirection(sortOrders,i)))

    return ret

client = connect_mongo()
database = client["general_news"]
repos = CrawlerRepos().connect(database)