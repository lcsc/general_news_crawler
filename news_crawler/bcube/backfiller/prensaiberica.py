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
        if first.date <= testDate and testDate <= last.date: return 0
        LOG.error(f"No se puede dar ({first.date}, {last.date}) ? {testDate}")
        return None


    def searchStartPage(self, context:BcubeArticleReaderContext,start:datetime)->Tuple[int,NewsPaperBackFill]:
        cat  =context.category

        cp=1
        # try with page=1
        # TODO handle this
        response = self._downloader.get_url_cat(context,1)
        if response.status_code!=200 or context.lastFound is None :
            #some pages gives error on page 1, try page2
            response =self._downloader.get_url_cat(context,2)
            cp=2
        if response.status_code != 200:
            return (None,NewsPaperBackFill(status=BfStatus_ERROR,msg="Sin Noticias (!200)"))
        
        if context.lastFound is None:
            return (None,NewsPaperBackFill(status=BfStatus_OK,msg="Sin Noticias"))
        
        LOG.debug(f"   Found {len(context.lastFound)}")
        
        first,last = self.extractFirstLastDates(context.lastFound)
        location = self.objetivePageLocation(first,last,start)
        
        context.pagesHelper[cp]={"first":first,"last":last,"location":location}
        tp:int=None
        lpp:int=0
        if location==0: return (cp,None)
        if location<=0: return (None,NewsPaperBackFill(status=BfStatus_OK,msg="Sin Noticias"))

        LOG.debug (f" page :{cp} ({first.date}, {last.date}) -> {start}")
        while location > 0:
            tp = cp+10
            response =self._downloader.get_url_cat(context,tp)
            
            while response.status_code!=200:
                tp = int((cp+tp)/2)
                if tp == cp: return (None,None)
            first,last = self.extractFirstLastDates(context.lastFound)
            location = self.objetivePageLocation(first,last,start)
            context.pagesHelper[tp]={"first":first,"last":last,"location":location}
            LOG.debug (f" page :{tp} ({first.date}, {last.date}) -> {start}")
            cp=tp
            if location >0 and tp > lpp:lpp=tp
        
        if location ==0:
            LOG.debug(f"Found going up: {tp}, ({first.date}, {last.date})? {start}")
            return (tp,None)
        
        LOG.debug("Nos hemos pasado")
        while location <0 and tp>lpp:

            tp = cp -1
            if tp in context.pagesHelper:
                LOG.debug("Found in helper")
                LOG.debug(f"({cp}) {context.pagesHelper[cp]['location']}")
                LOG.debug(f"({tp}) {context.pagesHelper[tp]['location']}")
                return (None,None)

            response =self._downloader.get_url_cat(context,tp)
            if response.status_code!=200:
                LOG.error("GAP")
                cp=tp

            first,last = self.extractFirstLastDates(context.lastFound)
            location = self.objetivePageLocation(first,last,start)
            context.pagesHelper[tp]={"first":first,"last":last,"location":location}
            if location==0: 
                LOG.debug(f"Found going down: {tp}, ({first.date}, {last.date})? {start}")
                return (tp,None)          
            cp=tp
        LOG.debug(f"cp: {cp} -> {context.pagesHelper[cp]['location']} ({context.pagesHelper[cp]['first'].date}, {context.pagesHelper[cp]['last'].date})? {start}")
        LOG.debug(f"tp: {cp+1} -> {context.pagesHelper[cp+1]['location']} ({context.pagesHelper[cp+1]['first'].date}, {context.pagesHelper[cp+1]['last'].date})? {start}")
        return (cp,None)


    def do_backFillNews_cat(self,context:BcubeArticleReaderContext,start:datetime,end:datetime )->NewsPaperBackFill:
        LOG.info(f"Backfilling cat {context.category.cat_name}")
        
        (sp,res) = self.searchStartPage(context,end)
        
        if context.getArticleCount()>0:
            self._repos.articles.save_many(context.getListArticles())

        if res is not None:
            return res

        if sp is None:
            LOG.debug("Start page not found")
            return None # TODO Ver este problema (No hay noticias)
        LOG.debug(f"Encontrada pagina {sp}")
        
        first=context.pagesHelper[sp]["first"]
        last=context.pagesHelper[sp]["last"]
        searchDir=self.objetivePageLocation(first,last,start)
        context.pagesHelper[sp]["searchDir"]=searchDir

        while searchDir>0:
            sp+=1
            if sp in context.pagesHelper:
                first=context.pagesHelper[sp]["first"]
                last=context.pagesHelper[sp]["last"]
                searchDir=self.objetivePageLocation(first,last,start)
                context.pagesHelper[sp]["searchDir"]=searchDir
            else:
                response =self._downloader.get_url_cat(context, sp)
                if response.status_code !=200:
                    LOG.debug("Hemos llegado al final")
                    return NewsPaperBackFill(status=BfStatus_PENDING)
                   
                first,last = self.extractFirstLastDates(context.lastFound)
                searchDir = self.objetivePageLocation(first,last,start)
                context.pagesHelper[sp]={"first":first,"last":last,"searchDir":searchDir}
            LOG.debug(f"{sp}, ({first.date}, {last.date})? {start}")


        return NewsPaperBackFill(status=BfStatus_OK)
    