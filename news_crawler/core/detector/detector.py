from ..model.newspaper import NewsPaper, NewsPaperRepository
from ..model.engine import NewsPaperEngine
from .detectors import DetectionState, WPDetector, BcubeDetector, JoomlaDetector, DrupalDetector, OpenNemasDetector, BloggerDetector,VocentoDetector
from requests import Response
from ...common.tools import get_url
from ...common.faildetect import check_fail

from typing import List,Tuple

changed_url={
"https://www.noticias24digital.com/":"True",
"https://www.aragonhoy.net/":"https://www.aragonhoy.es/",
"https://www.sahagundigital.com/":"True",
"https://www.segoviadirecto.com/":"True",
"https://www.eldiadezamora.es/":"True",
"https://www.el3devuit.cat/":"True",
"https://www.infocamp.cat/":"True",
"https://www.diariodejaraizdelavera.es/":"True",
"https://www.lugoxornal.gal/":"True",
"https://www.xornaldelemos.gal/":"True",
"https://www.xornaldevigo.gal/":"True",
"https://www.deia.com/":"True",
"https://www.noticiasdegipuzkoa.com/":"True",
"https://www.noticiasdealava.com/":"True",
"https://www.basaurihoy.net/":"https://urbiko.net/",
"https://www.alicantesport.com/":"https://iconicsport.es/",
"https://alacantextra.com/":"https://www.valenciaextra.com/",
"https://www.deniadigital.es/":"True",
}

def _check_url(url_in):
    if url_in in changed_url:
        if "True" == changed_url[url_in]:
            return url_in.replace("www.","")
        return changed_url[url_in]
    return url_in



class NewsPaperDetector():
    def __init__(self,repo:NewsPaperRepository):
        self._repo = repo
        self._detectors = [WPDetector(), BcubeDetector(),JoomlaDetector(),DrupalDetector(),OpenNemasDetector(),BloggerDetector(),VocentoDetector()] 
        pass

    def detect_many(self, allNp:List[NewsPaper]):
        for np in allNp:
            if np.engine is not None:  # already detected
                continue

            engine = self.detect_one(np)
            if engine is not None:
                np.engine = engine
            self._repo.save(np)
        pass
    def detect_all(self):
        allNp:List[NewsPaper] = self._repo.find_by({})
        self.detect_many(allNp)

    def try_url(self, url:str)->Tuple[Response,str]:
         try:
            response = get_url(url)
            return response,None
            
         except Exception as e:
            return None,check_fail(e)
         pass

    def detect_url(self,newsPaper:NewsPaper)->DetectionState:
        state = DetectionState(newsPaper)
        urls= []
        if newsPaper.real_url is not None:
            urls.append(newsPaper.real_url)
        if newsPaper.alt_urls is not None:
            for u in newsPaper.alt_urls:
                urls.append(_check_url(u))
                if u != urls[-1]:
                    urls.append(u)
        newsPaper.url_fails=None
        errors = { }
        for url in urls:
        
            response,fail = self.try_url(url)
            if response is not None and response.status_code == 200:
                state._reponse = response
                newsPaper.real_url = response.url
                if newsPaper.real_url.endswith("//"):
                    newsPaper.real_url=newsPaper.real_url[:-1]
                if not newsPaper.real_url.endswith("/"):
                    newsPaper.real_url=newsPaper.real_url+"/"

                #print(f"  URL {url} -> {response.url}")
                return state
               
            if response is not None:
                # if response.status_code == 403:
                #     print("### 403 ###")
                #     print(f" URL {url}")
                #     print(response.request.headers)
                #     print()
                #     print(f"  URL {url} -> {response.headers}")
                #     print()
                #     print(response.text)
                #     print("### 403 ###")
                errors[url] = f"Code: {response.status_code}"
            if fail is not None:
                errors[url] = fail
            if fail is None:
                errors[url] = "Unknown"
        if errors != {}:
            newsPaper.url_fails = errors

        return None
        
        

    def detect_one(self, newsPaper:NewsPaper)->NewsPaperEngine:
        
        state = self.detect_url(newsPaper)
        if state is None:
            return None
        
        for detector in self._detectors:
            engine = detector.detect(state)
            if engine is not None:
                return engine
        
        return None
        