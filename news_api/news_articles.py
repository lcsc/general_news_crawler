from fastapi import APIRouter, Query
from typing import Annotated, List, Optional
from .models import BaseRequest
from .shared import build_query, repos
from news_crawler.core.model import NewsArticle
from .shared import build_query, repos, serialize_document

import logging

LOG = logging.getLogger(__name__)


api_arti = APIRouter(prefix="/news")

@api_arti.get("/{ccaa}/{short_name}/", operation_id="news_list")
async def get_newspapers(ccaa:str,short_name:str)->List[NewsArticle]:
    mongoQuery={"np_ccaa":ccaa,"np_name":short_name}
    LOG.info(f"  Searchin {mongoQuery}")
    items = repos.articles.find_by(mongoQuery)
    return [serialize_document(item) for item in items]
