from .models import BaseRequest
from news_crawler.core.model import CrawlerRepos
from news_crawler.common.tools import connect_mongo


import logging

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

client = connect_mongo()
database = client["general_news"]
repos = CrawlerRepos().connect(database)