from ...core.backfiller.backfiller import BackFiller
from ...common.consts import ENGINE_ID_Vocento, SUBENGINE_ID_vc_v22
from ...common.consts import BfStatus_OK, BfStatus_ERROR
from ...core.model.newspaper import NewsPaper,NewsArticle, NewsPaperBackFill
from ...bcube.model.bcube import BcubeCategory
from ..downloader.vocento import VocentoDownloader, VocentoArticleReader, VocentoArticleReaderContext
from datetime import datetime, timezone

import json
import math


import logging

LOG = logging.getLogger(__name__)

def safe_before (test:datetime,limit:datetime)->bool:
    if test is None or limit is None:
        return False
    if test.tzinfo is None:
        test = test.replace(tzinfo=timezone.utc)
    if limit.tzinfo is None:
        limit = limit.replace(tzinfo=timezone.utc)
    return test < limit

class VocentoBackFiller(BackFiller):
    def __init__(self, repos):
        super().__init__(repos)
        self._engine=ENGINE_ID_Vocento
        self._sub_engine=SUBENGINE_ID_vc_v22
        self._downloader=VocentoDownloader(repos)
        self._reader=VocentoArticleReader(repos)


        
    def do_backFillNews_cat(self,context:VocentoArticleReaderContext,start:datetime,end:datetime )->NewsPaperBackFill:
        page = 0
        last_page = math.inf
        
        if end and context.category.first_article and safe_before(end,context.category.first_article):
            LOG.debug(f"  First article {context.category.first_article} after end {end}")
            return NewsPaperBackFill(status=BfStatus_OK,msg="Category articles before end date")
        
        while page < last_page:
            html = self._downloader.get_category_page(context.news_paper,context, context.category ,page,start,end)
            if html is None:
                LOG.error(f"Error getting page {page} for {context.news_paper.short_name} {context.category.cat_name}")
                return NewsPaperBackFill(status=BfStatus_ERROR,msg=f"Error getting page {page}")
            data = json.loads(html)
            articles = self._reader.get_articles(context, data["html"])
            LOG.debug(f"  Page {page+1}/{last_page} got {len(articles)} articles, total {context.getArticleCount()}")
            if len(articles) == 0:
                break
            
            for a in articles:
                if a.date is not None:
                    if start is not None and a.date < start:
                        LOG.debug(f"  Article {a.id} date {a.date} before start {start}")
                        return NewsPaperBackFill(status=BfStatus_ERROR,msg="Articles before start date")
                    if end is not None and a.date > end:
                        LOG.debug(f"  Article {a.id} date {a.date} after end {end}")
                        return NewsPaperBackFill(status=BfStatus_ERROR,msg="Articles after end date")

            last_page = data["krammerData"]["totalPages"]
            page += 1
        
        return NewsPaperBackFill(status=BfStatus_OK)
    
    def do_backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None)->NewsPaperBackFill:
        start,end  = self.get_range(year,month,day)
        #ctx = BcubeArticleReaderContext(news_paper=np)
        LOG.debug(f"  from {start} to {end}")
        cats_filter={'ccaa': np.ccaa, 'short_name': np.short_name}
        cats = self._repos.bCubeCategories.find_by(cats_filter)
        ret = NewsPaperBackFill(status=BfStatus_OK)

        isForce=self.isForceDate(month,day)
        isStoreBf = self.isStoreBfDate(month,day)

        # Nos lo traemos a memoria, para no tener problemas con el cursor
        cats = list(cats)
        i=1

        for cat in cats:
            res = None
            LOG.debug(f"Testing {cat.cat_name} ({i}/{len(cats)})")
            i+=1
            if cat.isBfDone(year,month) and not isForce:
                LOG.debug(f"Already Done")
                continue
        
            context = VocentoArticleReaderContext(np,cat)
            try:
                res = self.do_backFillNews_cat(context,start,end)
                

            except Exception as e:
                LOG.error(e,exc_info=True)
                res= NewsPaperBackFill(status=BfStatus_ERROR,msg=str(e))

            if context.getArticleCount()>0:
                self._repos.articles.save_many(context.getListArticles())    
            if res is None or res.status != BfStatus_OK:
                ret = NewsPaperBackFill(status=BfStatus_ERROR,msg="Categorias incompletas")
            if res is not None and isStoreBf:
                cat.addBfStatus(year,month,res.status,res.msg)
                self._repos.bCubeCategories.save(cat)
            
            #return ret

        return ret