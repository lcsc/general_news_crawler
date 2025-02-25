from ...core.fetcher.extractor import NewsArticleReaderContext, NewsArticleReader, NewsArticleReader
from ...core.model.newspaper import NewsPaper, NewsArticle
from ...core.model.repos import CrawlerRepos
from ...common.tools import np_base_path
from ..model.bcube import BcubeCategory
from bs4 import BeautifulSoup
from typing import List,Dict
from datetime import datetime

import logging
LOG = logging.getLogger(__name__)


class BcubeArticleReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper,category:BcubeCategory):
        super().__init__(news_paper)
        self.category=category
        self.last_page=1
        self.page_size={}
        self.pagesHelper:Dict[int,Dict]={}

class BcubeArticleReader(NewsArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def _extract_list_elements(self, context, object)->List[any]:
        json=object
        html = json["html"]
        doc = BeautifulSoup(html, 'lxml')
        return doc.find_all('article')
    
    def _save_list_article(self,context:BcubeArticleReaderContext,article:NewsArticle,raw:any):
        cat = context.category.cat_name
        if not cat.endswith("/"): cat =cat +"/"
        if not cat.startswith("/"): cat ="/"+ cat
        path =f"{np_base_path(context.news_paper)}{cat}{article.article_id}.list_raw"

        modDate = article.date
        if "dateModified" in article.engine_data:
            modDate = article.engine_data["dateModified"]
        self.repos.save_file(path, str(raw),'list',modDate)
        article.raw_data=path
        pass


