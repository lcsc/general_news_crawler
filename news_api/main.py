
from news_crawler.model.repos import CrawlerRepos
from news_crawler.model.newspaper import NewsPaper

from typing import List

from fastapi import FastAPI
from pymongo import MongoClient
import news_crawler.common.consts

# uvicorn --reload --port 5000 news_api.main:app

client = MongoClient("mongodb://host.docker.internal:27017",username='root',
                     password='example',)
database = client["general_news"]

repos = CrawlerRepos().connect(database)


app = FastAPI()

def serialize_document(doc):
    #doc["_id"] = str(doc["_id"])
    return doc

def build_query(ccaa:str=None,short_name:str=None,engine:str=None,sub_engine:str=None):
    ret = {}
    if ccaa is not None: ret.update({"ccaa":ccaa})
    if short_name is not None: ret.update({"short_name":short_name})
    if engine is not None: ret.update({"engine.engine":engine})
    if sub_engine is not None: ret.update({"engine.sub_engine":sub_engine})
    return ret

@app.get("/")
async def read_root():
    return {"mensaje": "¡Hola desde FastAPI!"}

@app.get("/options")
async def get_options():
    return {"ccaas":news_crawler.common.consts.ccaa,
            "engines":news_crawler.common.consts.engines,
            "sub_engines":news_crawler.common.consts.sub_engines}

@app.get("/np")
async def get_newspapers(engine:str=None,sub_engine:str=None)->List[NewsPaper]:
    query = build_query(engine=engine,sub_engine=sub_engine)
    items = repos.newspaper.find_by(query)
    return [serialize_document(item) for item in items]

@app.get("/np/{ccaa}")
async def get_newspapers_ccaa(ccaa:str,engine:str=None,sub_engine:str=None)->List[NewsPaper]:
    query = build_query(ccaa=ccaa, engine=engine,sub_engine=sub_engine)
    print(f"  Searchin {query}")
    items = repos.newspaper.find_by(query)
    return [serialize_document(item) for item in items]

@app.get("/np/{ccaa}/{short_name}")
async def get_newspaper_ccaa_name(ccaa:str,short_name)->NewsPaper:
    item = repos.newspaper.find_one_by({"ccaa":ccaa,"short_name":short_name})
    return serialize_document(item)
