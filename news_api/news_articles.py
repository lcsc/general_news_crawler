from fastapi import APIRouter, Query
from typing import Annotated, List, Optional
from .models import BaseRequest,NewsSearch,NewsSearchResult
from news_crawler.core.model import NewsArticle
from .shared import  repos, serialize_document,buildSort

import logging
from datetime import datetime
LOG = logging.getLogger(__name__)


api_arti = APIRouter(prefix="/news")


@api_arti.get("/{ccaa}/{short_name}/", operation_id="news_list")
async def get_newspapers(ccaa:str,short_name:str,query: Annotated[NewsSearch, Query()])->NewsSearchResult:
    mongoQuery={"np_ccaa":ccaa,"np_name":short_name}
    #mongoQuery.update({"date":{"$gt":datetime.fromisoformat("2025-02-01T00:00:00Z")}})

    ret = NewsSearchResult()

    if query.notAfter:
        if query.notAfter.time() == datetime.min.time():
            query.notAfter = query.notAfter.replace(hour=23,minute=59,second=59)
    
    LOG.debug(f" Not Before: {query.notBefore}")
    LOG.debug(f"  Not After: {query.notAfter}")

    if query.notBefore:
        if query.notAfter:
            mongoQuery.update({"date":{"$gt":query.notBefore,"$lt":query.notAfter}})
        else:
            mongoQuery.update({"date":{"$gt":query.notBefore}})
    elif query.notAfter:
        mongoQuery.update({"date":{"$lt":query.notAfter}})

    if query.category:
        mongoQuery.update({"categories":{"$in":query.category}})
    
    if query.headlineDrought:
        if "empty" in query.headlineDrought.lower():
            mongoQuery.update({"is_headline_drought": None})
        elif "true" in query.headlineDrought.lower():
            mongoQuery.update({"is_headline_drought": True})
        elif "false" in query.headlineDrought.lower():
            mongoQuery.update({"is_headline_drought": False})

    ret.results = repos.articles.get_collection().count_documents(mongoQuery)
    ret.items = repos.articles.find_by(mongoQuery, 
                                       limit=query.rowsPerPage,
                                       skip=query.rowsPerPage*(query.page-1),
                                       sort=buildSort(query.sortBy,query.sortType))
    ret.pages=int(ret.results/query.rowsPerPage) +1
    LOG.info(f"  Searchin {mongoQuery}")
    LOG.info(f" found {ret.results}")
    ret.items = [serialize_document(item) for item in ret.items]
    return ret 

@api_arti.get("/{ccaa}/{short_name}/{id}", operation_id="news_get")
async def get_newspapers(ccaa:str,short_name:str,id:str)->Optional[NewsArticle]:
    mongoQuery={"np_ccaa":ccaa,"np_name":short_name,"article_id":id}
    ret = repos.articles.find_one_by(mongoQuery)
    return ret