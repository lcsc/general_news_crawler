from bs4 import BeautifulSoup

from news_crawler.bcube.model.bcube import  BcubeCategory
from ...core.fetcher.extractor import NewsArticleReaderContext, NewsArticleReader, NewsArticleReader
from ...core.model.newspaper import NewsPaper, NewsArticle
from ...core.model.repos import CrawlerRepos

from typing import List,Dict
from ...common.tools import get_url

import time

import logging
LOG = logging.getLogger(__name__)


class VocentoArticleReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper,category:BcubeCategory): # category:BcubeCategory
        super().__init__(news_paper)
        self.category=category
        self.last_page=1
        self.first_404=None
        self.page_size={}
        self.pagesHelper:Dict[int,Dict]={}

class VocentoArticleReader(NewsArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def get_categories(self,page:any)->List[str]: # category:BcubeCategory
        doc = BeautifulSoup(page, 'lxml')
        h3 = doc.find_all('h3')
        cats = []
        for h in h3:
            txt  = h.get_text().strip().lower()
            if "mapa web" == txt:
                links = h.parent.find_all('a')
                for a in links:
                    href = a.get('href')
                    if href is not None and href.startswith('/'):
                        if href not in cats:
                            cats.append(href)   
                        else:
                            LOG.debug(f"  ignoring link {href} in mapa web")

        return cats


class VocentoDownloader():
    def __init__(self,reader:VocentoArticleReader):
        self._reader=reader
        pass

    def get_mapa_web(self,news_paper:NewsPaper):
        
        url = news_paper.real_url+"mapa-web.html"
        LOG.debug(f"Downloading mapa web for {news_paper.short_name} from {url}")

        response =get_url(url)
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(url)
                count+=1
        
        if response.status_code==200:
            return response.content
        return None