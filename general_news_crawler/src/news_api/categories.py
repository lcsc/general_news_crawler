from fastapi import APIRouter, Query
from typing import Annotated, List, Optional
from .models import BaseRequest
from news_crawler.bcube.model import BcubeCategory
from .shared import  repos, serialize_document,buildSort

import logging
from datetime import datetime
LOG = logging.getLogger(__name__)


api_cats = APIRouter(prefix="/cat")


@api_cats.get("/{ccaa}/{short_name}/", operation_id="cat_list")
async def get_categories(ccaa:str,short_name:str)->List[BcubeCategory]:
    mongoQuery={"ccaa":ccaa,"short_name":short_name}
    ret = repos.bCubeCategories.find_by(mongoQuery)
    ret = [serialize_document(item) for item in ret]
    return ret
