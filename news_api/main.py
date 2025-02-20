
from news_crawler.core.model.repos import CrawlerRepos
from news_crawler.core.model.newspaper import NewsPaper

from .models import BaseRequest, OptionsResult

from typing import List

from fastapi import FastAPI, APIRouter, Query

from typing import Annotated, Literal, Optional

from pymongo import MongoClient
import news_crawler.common.consts
from news_crawler import initLogger 
from news_crawler.common.tools import connect_mongo

import logging
initLogger()
LOG = logging.getLogger(__name__)
# uvicorn --reload --host 0.0.0.0 --port 5000 news_api.main:app
client = connect_mongo()

database = client["general_news"]

repos = CrawlerRepos().connect(database)


app = FastAPI(openapi_prefix="/news/api")
api_np = APIRouter(prefix="/np")

def serialize_document(doc):
    #doc["_id"] = str(doc["_id"])
    return doc


def build_query(ccaa:str=None,provincia:str=None,query:BaseRequest=None):
    ret = {}
    if ccaa is not None: ret.update({"ccaa":ccaa})
    if provincia is not None: ret.update({"provincia":provincia})
    if query is not None:
        if query.engine is not None: ret.update({"engine.engine":query.engine})
        if query.sub_engine is not None: ret.update({"engine.sub_engine":query.sub_engine})
    return ret

@app.get("/")
async def read_root():
    return {"mensaje": "¡Hola desde FastAPI!"}

@app.get("/options", operation_id="options")
async def get_options()->OptionsResult:
    LOG.debug(news_crawler.common.consts.ccaa)

    return {"ccaas":list(news_crawler.common.consts.ccaa),
            "provincias":news_crawler.common.consts.provincias,
            "engines":news_crawler.common.consts.engines,
            "sub_engines":news_crawler.common.consts.sub_engines}

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



app.include_router(api_np)
