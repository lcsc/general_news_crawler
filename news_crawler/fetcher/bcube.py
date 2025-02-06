from ..model.repos import CrawlerRepos
from ..model.newspaper import NewsPaper, NewsArticle
from ..model.bcube.bcube import BcubeCategory
from .extractor import NewsPaperExtractor,NewsArticleReaderContext,NewsArticleReader
from typing import List
from ..common.tools import print_exception, np_base_path, save_file
from ..common.dates import isValidDay
from ..common.consts import month_thresold
from bs4 import BeautifulSoup

import sys

class BcubeArticleReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper,category:BcubeCategory):
        super().__init__(news_paper)
        self.category=category
        self.last_page=1
        self.page_size={}

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
        save_file(path, str(raw))
        article.raw_data=path
        pass

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
                    self._np_repos.articles.save_many(cat_articles)
                    for a in cat_articles:
                        ctx_gobal.addArticle(a)

            except Exception as e:
                print_exception(e)
        ret = ctx_gobal.getListArticles()
        if len(ret)>0:
            
            return ret
        return None # None means this newspaper is not from this extractor

    def _fill_stats_process_articles(self,articles:List[NewsArticle],cats:dict):
        for arti in articles:
            if not isValidDay(arti.date): continue
            if "category" not in arti.engine_data:
                print("****** ERROR ****")
                print("  Articulo sin categoria")
                print(arti.model_dump())
                print("****** ERROR ****")
                continue
            cat_data = cats[arti.engine_data["category"]]
            cat:BcubeCategory = cat_data["cat"]
            months = cat_data["months"]
            if cat.first_article is None:
                cat.first_article=arti.date
            if cat.first_article>arti.date:
                cat.first_article=arti.date
            month = arti.date.strftime("%Y-%m")
            if month not in months:
                months.update({month:1})
            else:
                months[month] += 1

    def _fill_stats_process_cats(self,cats:List[dict],np_months:dict, np:NewsPaper):
        n_articles=0
        for cat in cats:
            cat_data:BcubeCategory = cats[cat]["cat"]
            
            if cat_data.first_article is None:
                continue # no tiene articulos
            
            months_data:dict=cats[cat]["months"]
            months = sorted(list(months_data.keys()))
            for m in months:
                if months_data[m] >= month_thresold:
                    if cat_data.first_month is None:
                        cat_data.first_month=m
                    if m < cat_data.first_month:
                        cat_data.first_month=m
                if m not in np_months:
                    np_months.update({m:0})
                np_months[m]+=months_data[m]


            self._np_repos.bCubeCategories.save(cat_data)
            if np.first_article is None:
                np.first_article=cat_data.first_article
            if np.first_article> cat_data.first_article:
                np.first_article=cat_data.first_article
            
            if cat_data.n_articulos is not None: # si no hay suficientes no se puede saber con seguridad y consideramos 0
                n_articles+=cat_data.n_articulos
            
        np.n_articulos=n_articles

    def fill_stats(self, np:NewsPaper):
        print(f"Computing stats of {np.short_name} - {np.ccaa}")
        cats:List[BcubeCategory] = self._np_repos.bCubeCategories.find_by({"ccaa":np.ccaa,
                                                           "short_name":np.short_name})
        cats={c.cat_name: {"cat":c, "months":{}} for c in cats}

        articles = self._np_repos.articles.find_by({"np_name": np.short_name,"np_ccaa": np.ccaa})
        self._fill_stats_process_articles(articles,cats)

        np_months={}
        self. _fill_stats_process_cats(cats,np_months,np)

        months = sorted(list(np_months.keys()))
        for m in months:
            if np_months[m] >= month_thresold:
                if np.first_month is None:
                    np.first_month=m
                if m < np.first_month:
                    np.first_month=m
        self._np_repos.newspaper.save(np)

    
  #{engine_data: {category:"/borrar-2/"}}