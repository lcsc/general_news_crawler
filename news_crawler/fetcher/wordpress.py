from ..common.consts import ENGINE_ID_WordPress, SUBENGINE_ID_wp_json
from ..common.tools import get_url, print_exception, np_base_path, save_file

from ..model.newspaper import NewsPaper, NewsArticle
from ..model.repos import CrawlerRepos

from .extractor import NewsPaperExtractor, NewsArticleReader, NewsArticleReaderContext


from typing import List
import requests


class WpReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper):
        super().__init__(news_paper)
        self._n_articles:int=None
        self._n_pages:int=None

class WpArticleReader(NewsArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def _extract_list_elements(self, context, object)->List[any]:
        print ("_extract_list_elements")
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

        ret = self.repos.articles.find_one_by({"np_ccaa":np.ccaa,
                                                    "np_name":np.short_name,
                                                    "article_id":article_id,
                                                    })
        if ret is None:
            ret = NewsArticle(id=None,
                        np_ccaa=np.ccaa,
                        np_name=np.short_name,
                        article_id=article_id,
                        ##
                        article_headline=data["title"],
                        article_url=data["data-url"],
                        date= date,
                        engine_id=f"{ENGINE_ID_WordPress}-{SUBENGINE_ID_wp_json}",
                        engine_data=data
            )
        else:
            ret.article_headline=data["title"]
            ret.article_url=data["data-url"]
            ret.date= date
            ret.engine_id=f"{ENGINE_ID_WordPress}-{SUBENGINE_ID_wp_json}"
            ret.engine_data=data
        return ret
    
        pass

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
        if response.status_code==200:
            json = response.json()
            articles =self._reader.extract_list(ctx,json)
            if articles is None:
                return response
        
        return response

    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        ctx = WpReaderContext(np)
        reponse = self._wp_get_url(ctx,1)

        if reponse.status_code!=200:
            if np.engine is None or np.engine.sub_engine is None:
                print("   The NewsPaper is not WP-Json")
            else:
                print("   Error downloading articles")
            return None
        if ctx._n_articles is None and 'x-wp-total' in response.headers: # en la mayoria viene, pero en algunos no
            n_articles=response.headers['x-wp-total']
            ctx._n_articles=n_articles
        if ctx._n_page is None and 'x-wp-totalpages' in reponse.headers:
            n_pages= reponse.headers['x-wp-totalpages']
            ctx._n_pages=n_pages
        
        


        np.n_articulos=ctx._n_articles
        ret = ctx.getListArticles()
        self._np_repos.articles.save_many(ctx.getListArticles())
        return ret
        
