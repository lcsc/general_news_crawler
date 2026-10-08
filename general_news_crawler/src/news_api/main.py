from .models import OptionsResult
from fastapi import FastAPI, APIRouter

import news_crawler.common.consts
from news_crawler import initLogger 

import logging
initLogger()
LOG = logging.getLogger(__name__)
# uvicorn --reload --host 0.0.0.0 --port 5000 news_api.main:app

# Importing the routers after logging is initialized
from .newspapers import api_np
from .news_articles import api_arti, api_arti_dro
from .categories import api_cats
from .files import api_files

app = FastAPI(openapi_prefix="/news/api")

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



app.include_router(api_np)
app.include_router(api_arti)
app.include_router(api_arti_dro)
app.include_router(api_cats)
app.include_router(api_files)