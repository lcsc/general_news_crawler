from ...core.backfiller.backfiller import BackFiller
from ...common.consts import ENGINE_ID_bCube
from ...common.consts import BfStatus_OK, BfStatus_ERROR
from ...core.model.newspaper import NewsPaper,NewsArticle, NewsPaperBackFill
from ..model.bcube import BcubeCategory
from ..downloader.bcube import BcubeArticleReaderContext 
from datetime import datetime
import logging

LOG = logging.getLogger(__name__)

class BcubeBackFiller(BackFiller):
    def __init__(self, repos, subengine:str):
        super().__init__(repos)
        self._engine=ENGINE_ID_bCube
        self._sub_engine=subengine


        
    def do_backFillNews_cat(self,context:BcubeArticleReaderContext,start:datetime,end:datetime )->NewsPaperBackFill:
        pass
    
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
        
            context = BcubeArticleReaderContext(np,cat)
            try:
                res = self.do_backFillNews_cat(context,start,end)
                
                #Este es un caso especial, que esta fallando esta categoria, la saltamos.   
                if cat.cat_name == "/elecciones/generales/" \
                    and np.ccaa == "canarias" \
                    and np.short_name =="eldia" \
                    and res.status !=BfStatus_OK:
                    res.status=BfStatus_OK

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


        return ret