from ...core.model.repos import CrawlerRepos
from ...core.model.newspaper import NewsArticle,NewsPaper,NewsPaperEngine, NewsPaperBackFill
from ...common.consts import BfStatus_OK
from ...common.dates import get_range


from typing import List,Tuple,Dict
from datetime import datetime,timedelta
import logging

LOG = logging.getLogger(__name__)

class BackFiller():
    def __init__(self, repos:CrawlerRepos):
        self._repos = repos
        self._engine:str=None
        self._sub_engine:str=None
    
    def isNewsPaperProcessable(self,np:NewsPaper)->bool:

        if np.engine is None: return False
        if np.engine.engine != self._engine: return False
        if np.engine.sub_engine != self._sub_engine: return False
        return True

    def isForceDate(self,month:int=None,day:int=None):
        return month is not None and day is not None
    
    def isStoreBfDate(self,month:int=None,day:int=None):
        return month is not None and day is None

    def get_range(self,year:int,month:int=None,day:int=None)->Tuple[datetime,datetime]:
        return get_range(year,month,day)
        

    def do_backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None)->NewsPaperBackFill:
        '''Should be implemented by subclases'''
        # return true if was ok and save mus be done
        return None

    def backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None):
        LOG.info(f"BackFilling News of ({np.short_name})\"{np.name}\"")

        if not self.isNewsPaperProcessable(np):
            # si nos invocan directamente mostramos warn
            LOG.warning(f"  {np.short_name} is not processable, forcing check...")

        if np.n_articulos is None:
            LOG.error("No tiene articulos, no se ha podido obtener informacion previa")
            return
        if np.first_article is None or np.first_month is None:
            LOG.error("Falta informacion previa")
            return
        
        res = self.do_backFillNews(np=np,year=year,month=month,day=day)
        if res is not None:
            if self.isStoreBfDate(month,day):
                np.addBfStatus(year,month,status=res.status,msg=res.msg)
            self._repos.newspaper.save(np)

    def backfillManyNews(self,newspapers:List[NewsPaper],year:int,month:int=None,day:int=None):
        for np in newspapers:
            if self.isNewsPaperProcessable(np):
                self.backFillNews(np=np,year=year,month=month,day=day)


class BackFillerManager(BackFiller):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos=repos)
        self._fillers:Dict[str,BackFiller]={}
        pass
    
    def _getFillerID(self,engine,sub_engine)->str:
        if sub_engine is None:sub_engine="None"
        return f"{engine}/{sub_engine}"
    
    def _getFillerIdNp(self,np:NewsPaper)->str:
        if np.engine is None:return "None"
        return self._getFillerID(np.engine.engine,np.engine.sub_engine)

    def addBackFiller(self,filler:BackFiller):
        self._fillers[self._getFillerID(filler._engine,filler._sub_engine)]=filler

    def _getBackFillerNewsPaper(self,np:NewsPaper)->BackFiller:
        filler_id = self._getFillerIdNp(np)
        if np.engine is not None:
            if filler_id in self._fillers:
                filler = self._fillers[filler_id]
                if filler.isNewsPaperProcessable(np):
                    return filler
        #si hemos llegado hasta aqui buscamos por todos a ver si alguno lo admite
        for id in self._fillers:
            filler = self._fillers[id]
            if filler.isNewsPaperProcessable(np):
                return filler
        LOG.debug(f"BackFiller Manager didn't found BackEnd for {np.short_name}:({filler_id})")
        #LOG.debug(self._fillers.keys())
        return None

    def isNewsPaperProcessable(self,np:NewsPaper)->bool:
        filler = self._getBackFillerNewsPaper(np)
        return filler is not None
    
    def backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None):
        filler = self._getBackFillerNewsPaper(np)
        if filler is not None:
            filler.backFillNews(np,year,month,day)
