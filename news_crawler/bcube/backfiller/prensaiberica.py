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

    def _estimateStartPage(self, tp:int,context:BcubeArticleReaderContext,start:datetime) -> int:
        if tp is None or tp <= 0:
            return None
        
        
        pages = list(context.pagesHelper.keys())
        if len(pages) == 1:
            return None
        
        pages = sorted(pages)
        itp = pages.index(tp)
        sp = pages[itp-1]
        
        

        LOG.debug(f"Estimating start page from {tp} to {sp}")
        f_start = context.pagesHelper[sp]["first"]
        l_start = context.pagesHelper[tp]["first"]
        
        LOG.debug(f"cp {sp} -> ({f_start.date})") 
        LOG.debug(f"tp {tp} -> ({l_start.date})")
        LOG.debug(f"start   -> ({start})")

        diff_time_pages = (f_start.date - l_start.date).total_seconds()
        diff_time_pages_page = diff_time_pages/(tp-sp)
        LOG.debug(f"tp-sp: {diff_time_pages} seconds -> {diff_time_pages_page} seconds per page")

        diff_times_sp = (f_start.date - start).total_seconds()
        if diff_time_pages_page == 0:
            LOG.debug("diff_time_pages_page is 0, returning 1")
            return 1
        LOG.debug(f"diff_times_sp: {diff_times_sp} seconds")
        page_obj = int(sp + diff_times_sp / diff_time_pages_page)
        LOG.debug(f"page_obj: {page_obj} pages")

        estimated_diff = page_obj - tp
        LOG.debug(f"page_obj_diff: {estimated_diff} pages")
        if estimated_diff <0 and estimated_diff >= -10: 
            return 0 # nos hemos pasado de pagina, pero no mucho
        
        factor = 0.8
        if estimated_diff > 10*(tp-sp):
            factor = min(0.8,abs((tp-sp)/100))        
            LOG.debug(f"Too much diff factor: {factor}")
        ret =  int(factor * estimated_diff)
        LOG.debug(f"ret: {ret} pages")
        return ret

    def _getlastPlusPage(self,context:BcubeArticleReaderContext)->int:
        page =  0
        for p in context.pagesHelper:
            if context.pagesHelper[p]["location"] > 0 and p> page:
                page = p
        return page
    
    def _getFisrtMinusPage(self,context:BcubeArticleReaderContext)->int:
        page =  None
        for p in context.pagesHelper:       
            if context.pagesHelper[p]["location"]  <0:
                if page is None:
                    page = p
                if p < page:
                    page = p

        return page
    
    def goAproximation(self,context:BcubeArticleReaderContext,start:datetime, cp:int)->Tuple[int, int, int]:
        LOG.debug(f"   Found {len(context.lastFound)}")
        
        first,last = self.extractFirstLastDates(context.lastFound)
        location = self.objetivePageLocation(first,last,start)
        
        context.pagesHelper[cp]={"first":first,"last":last,"location":location}
        tp:int=None
        lpp:int=0
        if location==0: return (cp,cp,location)
        if location<=0: return (cp,cp,location)

        #LOG.debug (f" page :{cp} ({first.date}, {last.date}) -> {start}")
        movement = self._estimateStartPage(cp,context,start)
        LOG.debug(f"Movement: {movement} pages")
        while movement !=0:
            if movement is None:
                movement = 10
            tp = int(cp+movement)

            tp = self._fixTpLimits(context, tp)
            
            LOG.debug(f"Checking page {tp}")
            if tp in context.pagesHelper:
                LOG.debug("Found in helper")

                #sacamos los valres de la pagina
                first = context.pagesHelper[tp]["first"]
                last = context.pagesHelper[tp]["last"]
                location = context.pagesHelper[tp]["location"]
                if tp == (context.first_404-1) and location >= 0:
                    # Aqui hemos llegado al incio de las publicaciones
                    return (None,None,location)
            else:
                LOG.debug(f"Not found in helper, trying {tp}")    
                response =self._downloader.get_url_cat(context,tp)
                while response.status_code!=200 or context.lastFound is None:
                    tp = int(tp-movement/10)
                    tp = self._fixTpLimits(context, tp)
                    # Aqui hemos llegado al incio de las publicaciones
                    # Nuestra fecha de incio puede ser anterior a la primera noticia
                    # Buscamos la ultima pagina con noticias
                    #LOG.debug(f"Respuesta no 200, probamos con {tp}")
                    if tp == cp:
                        # Hemos llegado a la ulima pagina (que ya hemos leido correctamente)
                        return (None,None,location)
                    response =self._downloader.get_url_cat(context,tp)

                first,last = self.extractFirstLastDates(context.lastFound)
                location = self.objetivePageLocation(first,last,start)
                context.pagesHelper[tp]={"first":first,"last":last,"location":location}

            #LOG.debug (f" page :{tp} ({first.date}, {last.date}) -> {start}")
            cp=tp
            if location >0 and tp > lpp:lpp=tp
            movement = self._estimateStartPage(cp,context,start)
        return (cp,lpp,location)

    def _fixTpLimits(self, context, tp):
        lastPlusPage = self._getlastPlusPage(context)
        if tp < lastPlusPage:
                # Si estimamos por debajo de la ultima pagina que nos pide subir,
                # Probamos con la siguente.
            LOG.debug(f"Page {tp} is less than lastOkPage")
            tp =lastPlusPage+1
        firstMinusPage = self._getFisrtMinusPage(context)
        if firstMinusPage is not None and tp > firstMinusPage:
                # Si estimamos por debajo de la primera pagina que nos pide bajar,
                # Probamos con la anterior.
            LOG.debug(f"Page {tp} is greater than firstMinusPage")
            tp = firstMinusPage-1

        if context.first_404 is not None and tp >= context.first_404:
            tp = context.first_404 -1
        return tp

    def _goUp(self,context:BcubeArticleReaderContext,start:datetime, cp:int)->Tuple[int, int, int]:
        LOG.debug(f"   Found {len(context.lastFound)}")
        
        first,last = self.extractFirstLastDates(context.lastFound)
        location = self.objetivePageLocation(first,last,start)
        
        context.pagesHelper[cp]={"first":first,"last":last,"location":location}
        tp:int=None
        lpp:int=0
        if location==0: return (cp,cp,location)
        if location<=0: return (cp,cp,location)

        #LOG.debug (f" page :{cp} ({first.date}, {last.date}) -> {start}")
    
        while location > 0:
            tp = cp+10
            response =self._downloader.get_url_cat(context,tp)
            
            while response.status_code!=200 or context.lastFound is None:
                tp = tp-1
                # Aqui hemos llegado al incio de las publicaciones
                # Nuestra fecha de incio puede ser anterior a la primera noticia
                # Buscamos la ultima pagina con noticias
                #LOG.debug(f"Respuesta no 200, probamos con {tp}")
                if tp == cp:
                    # Hemos llegado a la ulima pagina (que ya hemos leido correctamente)
                    return (None,None,location)
                response =self._downloader.get_url_cat(context,tp)

            first,last = self.extractFirstLastDates(context.lastFound)
            location = self.objetivePageLocation(first,last,start)
            context.pagesHelper[tp]={"first":first,"last":last,"location":location}
            #LOG.debug (f" page :{tp} ({first.date}, {last.date}) -> {start}")
            cp=tp
            if location >0 and tp > lpp:lpp=tp
        return (cp,lpp,location)
    

    def goDown(self,context:BcubeArticleReaderContext,start:datetime, cp:int, location:int, lpp:int)->int:
        tp=cp
        while location <0 and tp>lpp:
            tp = cp -1
            if tp in context.pagesHelper:
                LOG.debug("Found in helper")
                if context.pagesHelper[tp]['location']>=0:
                    return tp
                LOG.debug(f"({cp}) {context.pagesHelper[cp]['location']}")
                LOG.debug(f"({tp}) {context.pagesHelper[tp]['location']}")
                return None #TODO este caso 

            response =self._downloader.get_url_cat(context,tp)
            if response.status_code!=200:
                LOG.error("GAP")
                cp=tp

            first,last = self.extractFirstLastDates(context.lastFound)
            location = self.objetivePageLocation(first,last,start)
            context.pagesHelper[tp]={"first":first,"last":last,"location":location}
            if location==0: 
                LOG.debug(f"Found going down: {tp}, ({first.date}, {last.date})? {start}")
                return tp
            cp=tp
        #si llegamos aqui es que cp es 1 y cp+1 es -1, la fecha buscada se produce entre paginas
        return cp

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
        if response.status_code not in [200,404]: #un 404 es que no hay noticias
            return (None,NewsPaperBackFill(status=BfStatus_ERROR,msg=f"Sin Noticias ({response.status_code})"))
        
        if context.lastFound is None:
            return (None,NewsPaperBackFill(status=BfStatus_OK,msg="Sin Noticias"))
        
        (cp,lpp,location) = self.goAproximation(context,start,cp)

        if cp is None and location>0:
            # La fecha buscada es anterior a la primera noticia
            return (None,NewsPaperBackFill(status=BfStatus_OK,msg="Antes de la primera noticia"))

        if location ==0:
            LOG.debug(f"Found going up: {cp}, ({context.pagesHelper[cp]['first'].date}, {context.pagesHelper[cp]['last'].date})? {start}")
            return (cp,None)
        
        if cp is None:
            LOG.error("Going Up return None")

        LOG.debug("Nos hemos pasado")
        cp = self.goDown(context,start,cp,location,lpp)

        #LOG.debug(f"cp: {cp} -> {context.pagesHelper[cp]['location']} ({context.pagesHelper[cp]['first'].date}, {context.pagesHelper[cp]['last'].date})? {start}")
        #LOG.debug(f"tp: {cp+1} -> {context.pagesHelper[cp+1]['location']} ({context.pagesHelper[cp+1]['first'].date}, {context.pagesHelper[cp+1]['last'].date})? {start}")
        return (cp,None)

    def readPages(self,context:BcubeArticleReaderContext,start:datetime,sp:int) -> NewsPaperBackFill:
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
                if response.status_code ==404:
                    # Ya no hay mas noticias
                    LOG.debug("Hemos llegado al final")
                    return NewsPaperBackFill(status=BfStatus_OK) 
                if response.status_code !=200:
                    LOG.debug("Error, lo dejamos en Pending para otra")
                    return NewsPaperBackFill(status=BfStatus_PENDING)
                   
                first,last = self.extractFirstLastDates(context.lastFound)
                searchDir = self.objetivePageLocation(first,last,start)
                context.pagesHelper[sp]={"first":first,"last":last,"searchDir":searchDir}
            #LOG.debug(f"{sp}, ({first.date}, {last.date})? {start}")
        return NewsPaperBackFill(status=BfStatus_OK)

    def do_backFillNews_cat(self,context:BcubeArticleReaderContext,start:datetime,end:datetime )->NewsPaperBackFill:
        if context.category.cat_name is None \
            or context.category.cat_name == "":

            LOG.error("Category is None")
            return NewsPaperBackFill(status=BfStatus_OK,msg="Category is None")
        	
        LOG.info(f"Backfilling cat {context.category.cat_name}")
        
        (sp,res) = self.searchStartPage(context,end)
        
        if context.getArticleCount()>0:
            self._repos.articles.save_many(context.getListArticles())

        if res is not None:
            return res

        if sp is None:
            LOG.debug("Start page not found")
            return NewsPaperBackFill(status=BfStatus_ERROR,msg="Star Page is None") # TODO Ver este problema (No hay noticias)
        
        LOG.debug(f"Encontrada pagina {sp}")
        
        return self.readPages(context,start,sp)

    