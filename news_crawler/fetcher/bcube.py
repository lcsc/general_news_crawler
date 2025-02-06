from ..model.repos import CrawlerRepos
from ..model.newspaper import NewsPaper, NewsArticle
from ..model.bcube.bcube import BcubeCategory
from .extractor import NewsPaperExtractor,NewsArticleReaderContext,NewsArticleReader
from typing import List
from ..common.tools import print_exception
from bs4 import BeautifulSoup

class BcubeArticleReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper,category:BcubeCategory):
        super().__init__(news_paper)
        self.category=category

class BcubeArticleReader(NewsArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def _extract_list_elements(self, context, object)->List[any]:
        json=object
        html = json["html"]
        doc = BeautifulSoup(html, 'lxml')
        return doc.find_all('article')


class BCubeExtractor(NewsPaperExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        self._engine = "bCube"
        self._reader:BcubeArticleReader=None

    def get_categories(self,np:NewsPaper)->list[BcubeCategory]:
        return None

    def extract_one_category(self,np:NewsPaper,cat:BcubeCategory)->List[NewsArticle]:
        return None
    
    def _find_category(self,ccaa:str,short_name:str,cat_name:str)->BcubeCategory:
        return self._np_repos.bCubeCategories.find_one_by({"ccaa":ccaa,
                                                           "short_name":short_name,
                                                           "cat_name":cat_name})
    
    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        print(f"\nextracting {np.short_name}")
        categories = self.get_categories(np)
        # Si no hay categorias, no es de este extractor
        if categories is None:
            return None
        
        print(f"  found {len(categories)} categories")
        ctx_gobal=BcubeArticleReaderContext(np,None)
        for cat in categories:
            try:
                self._np_repos.bCubeCategories.save(cat)
                cat_articles = self.extract_one_category(np,cat)  
                self._np_repos.bCubeCategories.save(cat)
                if cat_articles is not None:
                    print(f"  [{cat.cat_name}] found {len(cat_articles)} articles")
                    self._np_repos.articles.save_many(ret)
                    for a in cat_articles:
                        ctx_gobal.addArticle(a)

            except Exception as e:
                print_exception(e)
        ret = ctx_gobal.getListArticles()
        if len(ret)>0:
            
            return ret
        return None # None means this newspaper is not from this extractor
