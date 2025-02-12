from ..common.consts import ENGINE_ID_WordPress, SUBENGINE_ID_wp_json
from ..common.tools import get_url, print_exception, np_base_path, save_file
from ..common.dates import isValidDay, find_first_month,build_monthly_histogram

from ..model.newspaper import NewsPaper, NewsArticle
from ..model.repos import CrawlerRepos

from .extractor import NewsPaperExtractor, NewsArticleReader, NewsArticleReaderContext

from datetime import datetime
from typing import List,Dict
import requests
import time
import sys

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
        path =f"{np_base_path(context.news_paper)}{article.article_id}.list_raw"
        save_file(path, str(raw))
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
            print(f"WARN: El articulo {article_id} no tiene fechas validas")

        ret = self.createOrUpdateArticle(np=np,
                                         article_id=article_id,
                                         engine_id=f"{ENGINE_ID_WordPress}-{SUBENGINE_ID_wp_json}",
                                         title=data["title"],
                                         url=data["data-url"],
                                         date=date,
                                         engine_data=data
                                         )

        return ret





class WordPressInfoExtractor(NewsPaperExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        self._engine = ENGINE_ID_WordPress
        self._subengine = SUBENGINE_ID_wp_json
        self._reader = WpArticleReader(repos)
    
    def _wp_get_url(self,ctx:WpReaderContext,page:int)->requests.Response:
        np = ctx.news_paper
        api_url = f"{np.real_url}wp-json/wp/v2/posts?page={page}&order=asc&orderby=date&per_page=50"
        response =get_url(api_url)
        
        #TODO: ver si alguna vez se cumple
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(api_url)
                count+=1
        if response.status_code==200:
            json = response.json()
            articles =self._reader.extract_list(ctx,json)
            if articles is None:
                return response
            ctx._histogram=build_monthly_histogram(articles,ctx._histogram)
            ctx._lastArticlesRead = articles
        
        return response
    def _get_number(self,n:int|str):
        if isinstance(n,int):
            return n
        
        if n.startswith("'"):
            n=n.replace("'","")
        try:
            return int(n)
        except Exception as e:
            print(f"WARN \"{n}\" is not a number ")
        return None
    
    def find_first_month(self,ctx:WpReaderContext)->str:
        print("Finding FM")
        first_month = find_first_month(histogram=ctx._histogram)
        page=1
        print(f" ({page}) {first_month}")
        cnt=ctx.getArticleCount()
        while first_month is None:
            page+=1
            
            response = self._wp_get_url(ctx,page)
            
            if response.status_code != 200:
                print("   Error getting articles")
                return first_month
            tmp = ctx.getArticleCount()
            if len(ctx._lastArticlesRead)==0:
                print("   No articles read")
                return first_month
            if tmp == cnt:
                print("  WARN no new articles found")

            first_month=find_first_month(ctx._histogram)
            print(f" ({page}) {first_month}")
            cnt=tmp
            
            
            
        return first_month

    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        print(f"Testing {np.short_name}")
        ctx = WpReaderContext(np)
        response = self._wp_get_url(ctx,1)

        if response.status_code!=200:
            if np.engine is None or np.engine.sub_engine is None:
                print("   The NewsPaper is not WP-Json")
            else:
                print("   Error downloading articles")
            return None
        
        if ctx._n_articles is None and 'x-wp-total' in response.headers: # en la mayoria viene, pero en algunos no
            n_articles=response.headers['x-wp-total']
            ctx._n_articles=self._get_number(n_articles)
        if ctx._n_pages is None and 'x-wp-totalpages' in response.headers:
            n_pages= response.headers['x-wp-totalpages']
            ctx._n_pages=self._get_number(n_pages)
        
        ret = ctx.getListArticles()
        if ret == None or len(ret)==0:
            print("  No Articles Found")
            return None
        print(f"  found {len(ret)} articles in page")


        np.n_articulos=ctx._n_articles
        np.first_month=self.find_first_month(ctx)
        print (f"  FM={np.first_month}")

        ret = ctx.getListArticles()
        self._np_repos.articles.save_many(ret)        
        sys.stdout.flush() #cada vez que terminemos una web
        return ret
    
    # def should_be_extracted(self,np:NewsPaper)->bool:
    #     print("Asking to be extracted")
    #     return True
