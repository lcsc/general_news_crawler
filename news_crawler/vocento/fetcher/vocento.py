from datetime import timezone
from news_crawler.bcube.model.bcube import BcubeCategory
from ...core.model.repos import CrawlerRepos
from ...core.model.newspaper import NewsPaper, NewsArticle

from ...core.fetcher.extractor import NewsPaperExtractor,NewsArticleReaderContext,NewsArticleReader
from typing import List
from ...common.tools import print_exception, np_base_path, save_file
from ...common.dates import isValidDay
from ...common.consts import month_thresold,ENGINE_ID_Vocento,SUBENGINE_ID_vc_v22


from ..downloader.vocento import VocentoArticleReader, VocentoArticleReaderContext, VocentoDownloader
import json
import logging
LOG= logging.getLogger(__name__)


class VocentoInfoExtractor(NewsPaperExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        self._engine = ENGINE_ID_Vocento
        self._subengine = SUBENGINE_ID_vc_v22
        self._reader = VocentoArticleReader(repos)
        self._downloader = VocentoDownloader(self._reader)

    def _find_category(self,ccaa:str,short_name:str,cat_name:str)->(BcubeCategory | None):
        return self._np_repos.bCubeCategories.find_one_by({"ccaa":ccaa,
                                                           "short_name":short_name,
                                                           "cat_name":cat_name})

    def get_categories(self,np:NewsPaper)->list[BcubeCategory]: # list[VocentoCategory]
        home_page = self._downloader.get_mapa_web(np)
        vcReader:VocentoArticleReader = self._reader # type: ignore
        cats = vcReader.get_categories(home_page)
        ret = []
        for c in cats:
            cat = self._find_category(np.ccaa,np.short_name,c)
            if cat is None:
                cat = BcubeCategory(ccaa=np.ccaa,
                                    provincia=np.provincia,
                                    short_name=np.short_name,
                                    cat_name=c,
                                    cat_url=np.real_url + c[1:] if c.startswith('/') else np.real_url + c,
                                    )
                self._np_repos.bCubeCategories.save(cat)
            else:
                LOG.debug(f"  category {c} already in DB")
            ret.append(cat)
        
        return ret
    

    def extract_one_category(self,np:NewsPaper,cat:BcubeCategory)->List[NewsArticle]:
        print(f"  Extracting {cat.cat_name}")
        context = VocentoArticleReaderContext(np,cat)
        vcReader:VocentoArticleReader = self._reader # type: ignore
        
        data_http = self._downloader.get_category_page(np,context,cat,0)
        #if data is not None:
        #    articles = vcReader.get_articles(data,context)
        #    return articles
        data = json.loads(data_http)
        if data is not None:
            #print(json.dumps(data, indent=2))
            cat.n_articulos = data["krammerData"]["total"]

            articles = vcReader.get_articles(context,data["html"])
            if len(articles)>0:
                # Update first article date
                articles = sorted(articles, key=lambda x: x.date)
                for a in articles:
                    if cat.first_article is None:
                        cat.first_article = a.date
                        cat.first_month = a.date.strftime("%Y-%m")
                    else:
                        if a.date.tzinfo is None:
                            a.date=a.date.replace(tzinfo=timezone.utc)
                        if cat.first_article.tzinfo is None:
                            cat.first_article=cat.first_article.replace(tzinfo=timezone.utc)
                        if a.date < cat.first_article:
                            cat.first_article = a.date
                            cat.first_month = a.date.strftime("%Y-%m")
                self._np_repos.articles.save_many(articles)
                return articles

        return None

    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        LOG.info(f"extracting {np.short_name} of {np.provincia}")
        categories = self.get_categories(np)
        # Si no hay categorias, no es de este extractor
        if categories is None:
            return None
        
        LOG.info(f"  found {len(categories)} categories")
        ctx_gobal=VocentoArticleReaderContext(np,None)
        for cat in categories:
            try:
                self._np_repos.bCubeCategories.save(cat)
                cat_articles = self.extract_one_category(np,cat)  
                self._np_repos.bCubeCategories.save(cat)
                if cat_articles is not None:
                    LOG.info(f"  [{cat.cat_name}] found {len(cat_articles)} articles")
                    self._np_repos.articles.save_many(cat_articles)
                    for a in cat_articles:
                        ctx_gobal.addArticle(a)
                    if cat.first_article is not None:
                        if np.first_article is None:
                            np.first_article = cat.first_article
                        else:
                            if np.first_article.tzinfo is None:
                                np.first_article=np.first_article.replace(tzinfo=timezone.utc)
                            if cat.first_article.tzinfo is None:
                                cat.first_article=cat.first_article.replace(tzinfo=timezone.utc)
                            if cat.first_article < np.first_article:
                                np.first_article = cat.first_article
                        np.first_month = np.first_article.strftime("%Y-%m")
                        if np.n_articulos is None:
                            np.n_articulos = 0
                        np.n_articulos += cat.n_articulos
            except Exception as e:
                print_exception(e)
            # Developement in progress stop here

        ret = ctx_gobal.getListArticles()
        if len(ret)>0:
            return ret
        
        return None # None means this newspaper is not from this extractor