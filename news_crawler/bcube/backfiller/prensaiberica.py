from .bcube import BcubeBackFiller
from ...common.consts import SUBENGINE_ID_bc_PrensaIberica
from ...common.consts import BfStatus_OK, BfStatus_ERROR, BfStatus_PENDING
from ...core.model.newspaper import NewsPaper,NewsArticle, NewsPaperBackFill
from ..downloader.prensaiberica import BcubePiDownloader, BcubePiArticleReader
from ..downloader.bcube import BcubeArticleReaderContext
from datetime import datetime
from ..model.bcube import BcubeCategory
from typing import List, Dict,Tuple
import logging

LOG = logging.getLogger(__name__)

class BcubePiBackFiller(BcubeBackFiller):
    def __init__(self, repos):
        super().__init__(repos,SUBENGINE_ID_bc_PrensaIberica)
        self._downloader=BcubePiDownloader(BcubePiArticleReader(repos))

    def extractFirstLastDates(self,articles:List[NewsArticle])->Tuple[datetime,datetime]:
        last:NewsArticle=None
        first:NewsArticle=None
        for arti in articles:
            if last is None: last=arti
            if first is None: first=arti

            if arti.date > last.date: last=arti
            if arti.date < first.date: first=arti

        return(first,last)
    
    def objetivePageLocation(self,first:NewsArticle,last:NewsArticle,testDate:datetime)->int:
        '''
         1 -> [testDate, first, last] -> (Test Date esta en el pasado -> aumentar pagina) 
         0 -> [first, testdate, last] -> en esta pagina se hace la transicion, Objetivo encontrado
        -1 -> [first, last, testDate] -> (Test date esta en el futuro -> Reducir pagina)
        '''
        if testDate < first.date: return 1
        if testDate > last.date: return -1
        if first.date >= testDate and testDate >= last.date: return 0
        return None


    def searchStartPage(self, context:BcubeArticleReaderContext,start:datetime)->int:
        cat  =context.category

        cp=1
        # try with page=1
        response = self._downloader.get_url_cat(context,1)
        if response.status_code!=200 or context.lastFound is None :
            #some pages gives error on page 1, try page2
            response =self._downloader.get_url_cat(context,2)
            cp=2
        if response.status_code != 200:
            return NewsPaperBackFill(status=BfStatus_ERROR,msg="Sin Noticias (!200)")
        
        if context.lastFound is None:
            return NewsPaperBackFill(status=BfStatus_OK,msg="Sin Noticias")
        
        LOG.debug(f"   Found {len(context.lastFound)}")
        
        first,last = self.extractFirstLastDates(context.lastFound)
        location = self.objetivePageLocation(first,last,start)
        helper:Dict[int,Dict]={}
        helper[cp]={"first":first,"last":last,"location":location}
        tp:int=None
        lpp:int=None
        if location==0: return cp
        while location > 0:
            tp = cp+10
            response =self._downloader.get_url_cat(context,2)
            
            while response.status_code!=200:
                tp = int((cp+tp)/2)
                if tp == cp: return None
            first,last = self.extractFirstLastDates(context.lastFound)
            location = self.objetivePageLocation(first,last,start)
            helper[tp]={"first":first,"last":last,"location":location}
            cp=tp
            if location >0 and tp > lpp:lpp=tp
        
        LOG.debug("Nos hemos pasado")
        if location==0: return cp
        while location <0 and tp>lpp:
            tp = cp -1



        return None


    def do_backFillNews_cat(self,np:NewsPaper,cat:BcubeCategory,start:datetime,end:datetime )->NewsPaperBackFill:
        LOG.info(f"Backfilling cat {cat.cat_name}")
        context = BcubeArticleReaderContext(np,cat)
        sp = self.searchStartPage(context,start)   

        if sp is None:
            LOG.debug("Start page not found")


        return NewsPaperBackFill(status=BfStatus_PENDING,msg="Pending")