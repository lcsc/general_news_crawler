from ...common.tools import get_url
from ...common.dates import build_monthly_histogram
from ...core.fetcher.extractor import NewsArticleReaderContext, NewsArticleReader, NewsArticleReader
from ...core.model.newspaper import NewsPaper, NewsArticle
from ...core.model.repos import CrawlerRepos
from ...common.consts import ENGINE_ID_WordPress, SUBENGINE_ID_wp_json
from ...common.dates import isValidDay
from ...common.tools import np_base_path, save_file

from typing import List,Dict
import time
import requests
from datetime import datetime

import logging
LOG = logging.getLogger(__name__)


class WpReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper):
        super().__init__(news_paper)
        self._n_articles:int=None
        self._n_pages:int=None
        self._histogram:Dict[str,int]={}
        self._lastArticlesRead:List[NewsArticle]=None

class WpArticleReader(NewsArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def _extract_list_elements(self, context, object)->List[any]:
        return object

    def _save_list_article(self,context:WpReaderContext,article:NewsArticle,raw:any):
        path =f"{np_base_path(context.news_paper)}/{article.article_id}.list_raw"
        #save_file(path, str(raw))
        self.repos.save_file(path,str(raw),"list",article.engine_data["modified_gmt"])
        article.raw_data=path
        pass

    def _extract_list_one(self,context:WpReaderContext,object:any)->NewsArticle:
        
        np = context.news_paper
        article_id =str(object['id'])
        data={}
        data["id"]=article_id
        data["title"]=object["title"]["rendered"]
        data["date"]=object["date"]
        data["date_gmt"]=object["date_gmt"]
        data["modified"]=object["modified"]
        data["modified_gmt"]=object["modified_gmt"]
        data["data-url"]=object["link"]
        date = data["date_gmt"]
        if not isValidDay(date):
            date=data["modified_gmt"]
        if not isValidDay(date):
            LOG.warning(f"WARN: El articulo {article_id} no tiene fechas validas")

        ret = self.createOrUpdateArticle(np=np,
                                         article_id=article_id,
                                         engine_id=f"{ENGINE_ID_WordPress}-{SUBENGINE_ID_wp_json}",
                                         title=data["title"],
                                         url=data["data-url"],
                                         date=date,
                                         engine_data=data
                                         )

        return ret

class WpDownlader():
    def __init__(self,reader:WpArticleReader):
        self._reader=reader
        pass

    def _get_number(self,n:int|str):
        if isinstance(n,int):
            return n
        
        if n.startswith("'"):
            n=n.replace("'","")
        try:
            return int(n)
        except Exception as e:
            LOG.warning(f"WARN \"{n}\" is not a number ")
        return None
    
    def _do_wp_get_url(self,
            ctx:WpReaderContext,
            api_url:str)->requests.Response:
        response =get_url(api_url)
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(api_url)
                count+=1
        
        if response.status_code==200:
            if ctx._n_articles is None and 'x-wp-total' in response.headers: # en la mayoria viene, pero en algunos no
                n_articles=response.headers['x-wp-total']
                n_articles=self._get_number(n_articles)
                if ctx._n_articles is None or n_articles > ctx._n_articles:
                    ctx._n_articles=n_articles
            if ctx._n_pages is None and 'x-wp-totalpages' in response.headers:
                n_pages= response.headers['x-wp-totalpages']
                n_pages= self._get_number(n_pages)
                if ctx._n_pages is None or n_pages > ctx._n_pages:
                    ctx._n_pages=n_pages

            json = response.json()         
            articles =self._reader.extract_list(ctx,json)
            
            if articles is None:
                return response
            ctx._histogram=build_monthly_histogram(articles,ctx._histogram)
            ctx._lastArticlesRead = articles
           

        
        return response
        

    def wp_get_url(self,ctx:WpReaderContext,page:int)->requests.Response:
        np = ctx.news_paper
        api_url = f"{np.real_url}wp-json/wp/v2/posts?page={page}&order=asc&orderby=date&per_page=50"
        return self._do_wp_get_url(ctx,api_url)
    

    def wp_get_dates(self,ctx:WpReaderContext,page:int,start:datetime,end:datetime)->requests.Response:
        np = ctx.news_paper
        timefilter=f"before={end.isoformat().replace('+','%2B')}"
        timefilter=f"{timefilter}&after={start.isoformat().replace('+','%2B')}"
        api_url = f"{np.real_url}wp-json/wp/v2/posts?page={page}&{timefilter}&order=desc&orderby=date&per_page=50"
        return self._do_wp_get_url(ctx,api_url)
    
