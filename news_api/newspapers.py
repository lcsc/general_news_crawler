from fastapi import APIRouter, Query
from typing import Annotated, List, Optional
from .models import NewsPaperSearch, NewsPaperResult
from .shared import build_query, repos
from news_crawler.core.model import NewsPaper
from .shared import build_query, repos, serialize_document, buildSort

import logging

LOG = logging.getLogger(__name__)

api_np = APIRouter(prefix="/np")

@api_np.get("/", operation_id="np_list")
async def get_newspapers(query: Annotated[NewsPaperSearch, Query()])->NewsPaperResult:
    LOG.info("Entrando")
    mongoQuery = build_query(query=query)
    ret = NewsPaperResult()
    ret.results = repos.newspaper.get_collection().count_documents(mongoQuery)
    ret.items = repos.newspaper.find_by(mongoQuery, 
                                       limit=query.rowsPerPage,
                                       skip=query.rowsPerPage*(query.page-1),
                                       sort=buildSort(query.sortBy,query.sortType))
    ret.pages=int(ret.results/query.rowsPerPage) +1
    LOG.info(f" found {ret.results}")
    ret.items = [serialize_document(item) for item in ret.items]
    return ret

@api_np.get("/{ccaa}/", operation_id="np_list_ccaa")
async def get_newspapers_ccaa(ccaa:str,query: Annotated[NewsPaperSearch, Query()])->NewsPaperResult:
    mongoQuery = build_query(ccaa=ccaa, query=query)
    LOG.info(f"  Searchin {mongoQuery}")

    ret = NewsPaperResult()
    ret.results = repos.newspaper.get_collection().count_documents(mongoQuery)
    ret.items = repos.newspaper.find_by(mongoQuery, 
                                       limit=query.rowsPerPage,
                                       skip=query.rowsPerPage*(query.page-1),
                                       sort=buildSort(query.sortBy,query.sortType))
    ret.pages=int(ret.results/query.rowsPerPage) +1
    LOG.info(f" found {ret.results}")
    ret.items = [serialize_document(item) for item in ret.items]

    return ret

@api_np.get("/{ccaa}/{provincia}/", operation_id="np_list_ccaa_prov")
async def get_newspaper_ccaa_provincia(ccaa:str,provincia:str,query: Annotated[NewsPaperSearch, Query()])->NewsPaperResult:
    LOG.info("Entrando")
    mongoQuery=build_query(ccaa=ccaa,provincia=provincia,query=query)
    ret = NewsPaperResult()
    ret.results = repos.newspaper.get_collection().count_documents(mongoQuery)
    ret.items = repos.newspaper.find_by(mongoQuery, 
                                       limit=query.rowsPerPage,
                                       skip=query.rowsPerPage*(query.page-1),
                                       sort=buildSort(query.sortBy,query.sortType))
    ret.pages=int(ret.results/query.rowsPerPage) +1
    LOG.info(f" found {ret.results}")
    ret.items = [serialize_document(item) for item in ret.items]

    return ret

@api_np.get("/{ccaa}/{provincia}/{short_name}/", operation_id="np_get")
async def get_newspaper_ccaa_name(ccaa:str,provincia:str,short_name:str)->Optional[NewsPaper]:
    if provincia == '*':provincia=None
    mongoQuery=build_query(ccaa=ccaa,provincia=provincia)
    LOG.info(f"  Searchin {mongoQuery}")
    
    mongoQuery.update({"short_name":short_name})
    item = repos.newspaper.find_one_by(mongoQuery)
    return serialize_document(item)
