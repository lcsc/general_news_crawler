from ..model.newspaper import NewsPaper,NewsArticle
from typing import List,Dict
from ..common.tools import print_exception
from ..model.repos import CrawlerRepos

class NewsArticleReaderContext():
    def __init__(self,news_paper:NewsPaper):
        self.news_paper:NewsPaper=news_paper
        self.articles:Dict[str,NewsArticle]={}

    def addArticle(self,article:NewsArticle):
        if article.article_id not in self.articles:
            self.articles[article.article_id]=article
        else:
            if article.article_url==self.articles[article.article_id].article_url: return
            print ("****** ID Repetido ******")
            print(article)
            print(self.articles[article.article_id])
    
    
    def getListArticles(self)->List[NewsArticle]:
        return list(self.articles.values())

class NewsArticleReader():
    def __init__(self,repos:CrawlerRepos):
        self.repos=repos

    def _extract_list_one(self,context:NewsArticleReaderContext,object:any)->NewsArticle:
        '''Cada clase debe implementar'''
        pass

    def _extract_list_elements(self,context:NewsArticleReaderContext,object:any)->List[any]:
        '''Cada clase debe implementar'''
        pass
    def extract_list(self,context:NewsArticleReaderContext,object:any)->List[NewsArticle]:
        list_news = self._extract_list_elements(context,object)
        for obj in list_news:
            article = self._extract_list_one(context,obj)
            if article is not None:
                context.addArticle(article)
        
        ret = context.getListArticles()
        if len(ret)==0: return None
        return ret

class NewsPaperExtractor():

    def __init__(self,np_repos:CrawlerRepos):
        self._np_repos = np_repos
        self._engine:str = None
        self._subengine:str = None
        self._reader:NewsArticleReader = None
    
    def get_no_engine(self):
        return self._np_repos.newspaper.find_by({"engine":None,"real_url":{"$ne":None}})
    
    def get_engine_no_subengine(self):
        return self._np_repos.newspaper.find_by({"engine.engine":self._engine,"engine.subengine":None})
    
    def get_engine_subengine(self):
        if self._subengine is None:
            return []
        return self._np_repos.newspaper.find_by({"engine.engine":self._engine,"engine.subengine":self._subengine})

    def get_candidates(self)->List[NewsPaper]:
        '''

        '''
        ret = []
        ret.extend(self.get_no_engine())
        if self._engine is not None:
            ret.extend(self.get_engine_no_subengine())
            if self._subengine is not None:
                ret.extend(self.get_engine_subengine())
        return ret


    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        # should be implemented by the subclasses
        # has to extract n_articles,
        # First declared news
        # First Month with 20+ articles
        return None

    def should_be_extracted(self,np:NewsPaper)->bool:
        # TODO Implement a basic filter
        return True
    
    def _process_one(self, np:NewsPaper):
        articles = self.extract_one(np)
        if articles is not None:
            print(f"  found {len(articles)} articles")
            self._np_repos.articles.save_many(articles)


    def extract_all(self):
        cand= self.get_candidates()
        for np in cand:
            if self.should_be_extracted(np):
                try:
                    self._process_one(np)
                except Exception as e:
                    print_exception(e)
