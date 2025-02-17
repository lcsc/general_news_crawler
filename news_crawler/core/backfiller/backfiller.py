from ...core.model.repos import CrawlerRepos
from ...core.model.newspaper import NewsArticle,NewsPaper,NewsPaperEngine, NewsPaperBackFill
from ...common.consts import BfStatus_OK


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


    def get_range(self,year:int,month:int=None,day:int=None)->Tuple[datetime,datetime]:
        '''
        Convierte los parametros de usuaro en un rango de comienzo fin
        return (comienzo,fin)
        '''
        if month is None:
            LOG.debug("Nos solicitan un Año")
            #2017-02-01T15:12:09.000Z
            start = datetime.fromisoformat(f"{year}-01-01T00:00:00Z")
            end = datetime.fromisoformat(f"{year+1}-01-01T00:00:00Z")-timedelta(seconds=1)
            return (start,end)
        if day is None:
            LOG.debug("Nos solicitan un Mes")
            #2017-02-01T15:12:09.000Z
            start = datetime.fromisoformat(f"{year}-{month:02}-01T00:00:00Z")
            if month==12:
                end = datetime.fromisoformat(f"{year+1}-01-01T00:00:00Z")-timedelta(seconds=1)
            else:
                end = datetime.fromisoformat(f"{year}-{month+1:02}-01T00:00:00Z")-timedelta(seconds=1)
            return (start,end)
        start = datetime.fromisoformat(f"{year}-{month:02}-{day:02}T00:00:00Z")
        end = start+timedelta(days=1)-timedelta(seconds=1)
        return (start,end)
        

    def do_backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None)->NewsPaperBackFill:
        '''Should be implemented by subclases'''
        # return true if was ok and save mus be done
        return None

    def backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None):
        if not self.isNewsPaperProcessable(np):
            # si nos invocan directamente mostramos warn
            LOG.warning(f"  {np.short_name} is not processable, forcing check...")
        res = self.do_backFillNews(np=np,year=year,month=month,day=day)
        if res is not None:
            if day is None and month is not None:
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
        return None

    def isNewsPaperProcessable(self,np:NewsPaper)->bool:
        filler = self._getBackFillerNewsPaper(np)
        return filler is not None
    
    def backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None):
        filler = self._getBackFillerNewsPaper(np)
        if filler is not None:
            filler.backFillNews(np,year,month,day)
