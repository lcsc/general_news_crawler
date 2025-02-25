from ...core.backfiller.backfiller import BackFiller
from ...common.consts import ENGINE_ID_bCube
from ...common.consts import BfStatus_OK, BfStatus_ERROR
from ...core.model.newspaper import NewsPaper,NewsArticle, NewsPaperBackFill
from ..model.bcube import BcubeCategory
from datetime import datetime
import logging

LOG = logging.getLogger(__name__)

class BcubeBackFiller(BackFiller):
    def __init__(self, repos, subengine:str):
        super().__init__(repos)
        self._engine=ENGINE_ID_bCube
        self._sub_engine=subengine


        
    def do_backFillNews_cat(self,np:NewsPaper,cat:BcubeCategory,start:datetime,end:datetime )->NewsPaperBackFill:
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

        for cat in cats:
            res = None
            if cat.isCatDone(year,month) and not isForce:
                continue
                
            res = self.do_backFillNews_cat(np,cat,start,end)
            if res is None or res.status != BfStatus_OK:
                ret = NewsPaperBackFill(status=BfStatus_ERROR,msg="Categorias incompletas")
            if res is not None and isStoreBf:
                cat.addBfStatus(year,month,res.status,res.msg)
                self._repos.bCubeCategories.save(cat)

        return ret