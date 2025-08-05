from ..model.newspaper import NewsPaper,NewsArticle
from typing import List,Dict, Optional
from ...common.tools import print_exception
from ..model.repos import CrawlerRepos
from ..model.engine import NewsPaperEngine
from datetime import datetime,timezone
from ...common.dates import delta_to_check, fecha_minima

import logging
LOG = logging.getLogger(__name__)


class NewsArticleReaderContext():
    def __init__(self,news_paper:NewsPaper):
        self.news_paper:NewsPaper=news_paper
        self.articles:Dict[str,NewsArticle]={}
        self.lastFound:Optional[List[NewsArticle]]=None

    def addArticle(self,article:NewsArticle):
        if article.article_id not in self.articles:
            self.articles[article.article_id]=article
        else:
            if article.article_url==self.articles[article.article_id].article_url: return
            LOG.error("****** ID Repetido ******")
            LOG.error(article)
            LOG.error(self.articles[article.article_id])
    
    
    def getListArticles(self)->List[NewsArticle]:
        return list(self.articles.values())
    
    def getArticleCount(self)->int:
        return len(self.articles.keys())

class NewsArticleReader():
    def __init__(self,repos:CrawlerRepos):
        self.repos=repos

    def _extract_list_one(self,context:NewsArticleReaderContext,object:any)->NewsArticle:
        '''Cada clase debe implementar'''
        pass

    def _extract_list_elements(self,context:NewsArticleReaderContext,object:any)->List[any]:
        '''Cada clase debe implementar'''
        pass

    def _save_list_article(self,context:NewsArticleReaderContext,article:NewsArticle,raw:any):
        '''Cada clase debe implementar'''
        pass

    def extract_list(self,context:NewsArticleReaderContext,object:any)->List[NewsArticle]:
        list_news = self._extract_list_elements(context,object)
        ret = []
        for obj in list_news:
            article = self._extract_list_one(context,obj)
            if article is not None:
                context.addArticle(article)
                self._save_list_article(context,article,obj)
                ret.append(article)
        
        #ret = context.getListArticles()
        if len(ret)==0: return None
        return ret
    
    def createOrUpdateArticle(self,
                              np:NewsPaper,
                              article_id:str,
                              engine_id:str,
                              title:str,
                              url:str,
                              date:str|datetime,
                              engine_data=any,
                              categories:List[str]=None
                              )->NewsArticle:
        if isinstance(date,str):
            if date.startswith("-"):
                date=fecha_minima
            else:
                date= datetime.fromisoformat(date)

        ret = self.repos.articles.find_one_by({"np_ccaa":np.ccaa,
                                                    "np_name":np.short_name,
                                                    "article_id":article_id,
                                                    })
        if ret is None:
            ret =NewsArticle( id=None,
                        np_ccaa=np.ccaa,
                        np_name=np.short_name,
                        np_provincia=np.provincia,
                        article_id=article_id,
                        ##
                        article_headline=title,
                        article_url=url,
                        date= date,
                        engine_id=engine_id,
                        engine_data=engine_data,
                        categories=categories
            )
        else:
            ret.article_headline=title
            ret.article_url=url
            ret.date= date
            ret.engine_id=engine_id
            ret.engine_data=engine_data
            if categories is not None:
                if ret.categories is None:
                    ret.categories=[]
                for cat in categories:
                    if cat not in ret.categories: 
                        ret.categories.append(cat)

        return ret
    
        

class NewsPaperExtractor():

    def __init__(self,np_repos:CrawlerRepos):
        self._np_repos = np_repos
        self._engine:str = None
        self._subengine:str = None
        self._reader:NewsArticleReader = None
    
    def get_no_engine(self, filter:Dict[str,str]=None):
        query = {}
        if filter is not None:
            query.update(filter)
        if "engine.engine" in query: query.pop('engine.engine')
        if "engine.sub_engine" in query: query.pop('engine.sub_engine')

        query.update({"engine":None,"real_url":{"$ne":None}})
        
        LOG.debug(f" Quering no Engine: {query}")
        return self._np_repos.newspaper.find_by(query)
    
    def get_engine_no_subengine(self, filter:Dict[str,str]=None):

        query = {}
        if filter is not None:
            query.update(filter)
        if "engine.engine" in query: query.pop('engine.engine')
        if "engine.sub_engine" in query: query.pop('engine.sub_engine')

        query.update({"engine.engine":self._engine,"engine.sub_engine":None})
        
        LOG.debug(f" Quering no SubEngine: {query}")

        return self._np_repos.newspaper.find_by(query)
    
    def get_engine_subengine(self, filter:Dict[str,str]=None):
        if self._subengine is None:
            return []  

        query = {}
        if filter is not None:
            query.update(filter)
        if "engine.engine" in query: query.pop('engine.engine')
        if "engine.sub_engine" in query: query.pop('engine.sub_engine')
        
        query.update({"engine.engine":self._engine,"engine.sub_engine":self._subengine})
        
        LOG.debug(f" Quering no Engine: {query}")
        return self._np_repos.newspaper.find_by(query)
    

    def get_candidates(self,try_no_engine=True,try_no_subengine:bool=None, filter:Dict[str,str]=None)->List[NewsPaper]:
        '''

        '''

        if filter is not None and "engine.sub_engine" in filter and filter["engine.sub_engine"] != self._subengine:
            LOG.warning("Omiting get_candidates")
            return []

        if try_no_subengine is  None: 
            try_no_subengine=try_no_engine
        
        ret = []

        if try_no_engine:
            ret.extend(self.get_no_engine(filter=filter))

        if self._engine is not None:
            if try_no_subengine:
                ret.extend(self.get_engine_no_subengine(filter=filter))
            if self._subengine is not None:
                ret.extend(self.get_engine_subengine(filter=filter))
        LOG.info(f"candidates to check: {len(ret)}")
        return ret


    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        # should be implemented by the subclasses
        # has to extract n_articles,
        # First declared news
        # First Month with 20+ articles
        return None

    def should_be_extracted(self,np:NewsPaper)->bool:
        if np.first_article is None : return True
        if np.first_month is None : return True
        if np.n_articulos is None : return True
        if np.last_check is None : return True
        date = datetime.now(tz=timezone.utc)

        if np.last_check.tzinfo is None:
            np.last_check=np.last_check.replace(tzinfo=timezone.utc)
        
        return date-np.last_check>delta_to_check
    
    def fill_stats(self, np:NewsPaper):
        # should be implemented by the subclasses
        pass

    def _process_one(self, np:NewsPaper)->bool:
        date = datetime.now(tz=timezone.utc)
        articles = self.extract_one(np)
        if articles is None:
            return False
        LOG.info(f"  found {len(articles)} articles")
        self._np_repos.articles.save_many(articles)
        if np.engine is None:
            np.engine=NewsPaperEngine(engine=self._engine,
                                      sub_engine=self._subengine,
                                      evidence={"articles_found":len(articles)})
        if np.engine.sub_engine is None:
            np.engine.sub_engine=self._subengine
        np.last_check=date
        self._np_repos.newspaper.save(np)
        return True

    def extract_many(self, cand:list[NewsPaper],force:bool=False):
        top = len(cand)
        for idx,np in enumerate(cand):
            LOG.info(f"[{idx+1}/{top}] Checking \"{np.name}\"")
            if force or self.should_be_extracted(np):
                try:
                    if self._process_one(np):
                        self.fill_stats(np)
                        self._np_repos.newspaper.save(np)
                except Exception as e:
                    print_exception(e)
    
    
    def extract_all(self,try_no_engine=True,try_no_subengine:bool=None, force:bool=False):

        cand= self.get_candidates(try_no_engine=try_no_engine,try_no_subengine=try_no_subengine)
        self.extract_many(cand)
