from fastapi import APIRouter, Query
from typing import Annotated, List, Optional
from .models import BaseRequest
from .shared import build_query, repos
from news_crawler.core.model import NewsPaper
from .shared import build_query, repos, serialize_document

import logging

LOG = logging.getLogger(__name__)

api_np = APIRouter(prefix="/np")

@api_np.get("/", operation_id="np_list")
async def get_newspapers(query: Annotated[BaseRequest, Query()])->List[NewsPaper]:
    mongoQuery = build_query(query=query)
    items = repos.newspaper.find_by(mongoQuery)
    return [serialize_document(item) for item in items]

@api_np.get("/{ccaa}/", operation_id="np_list_ccaa")
async def get_newspapers_ccaa(ccaa:str,query: Annotated[BaseRequest, Query()])->List[NewsPaper]:
    mongoQuery = build_query(ccaa=ccaa, query=query)
    LOG.info(f"  Searchin {mongoQuery}")
    items = repos.newspaper.find_by(mongoQuery)
    return [serialize_document(item) for item in items]

@api_np.get("/{ccaa}/{provincia}/", operation_id="np_list_ccaa_prov")
async def get_newspaper_ccaa_provincia(ccaa:str,provincia:str,query: Annotated[BaseRequest, Query()])->List[NewsPaper]:
    LOG.info("Entrando")
    mongoQuery=build_query(ccaa=ccaa,provincia=provincia,query=query)
    LOG.info(f"  Searchin {mongoQuery}")
    items = repos.newspaper.find_by(mongoQuery)
    return [serialize_document(item) for item in items]

@api_np.get("/{ccaa}/{provincia}/{short_name}/", operation_id="np_get")
async def get_newspaper_ccaa_name(ccaa:str,provincia:str,short_name:str)->Optional[NewsPaper]:
    if provincia == '*':provincia=None
    mongoQuery=build_query(ccaa=ccaa,provincia=provincia)
    LOG.info(f"  Searchin {mongoQuery}")
    
    mongoQuery.update({"short_name":short_name})
    item = repos.newspaper.find_one_by(mongoQuery)
    return serialize_document(item)
