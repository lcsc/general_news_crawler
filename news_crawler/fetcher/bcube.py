from ..model.newspaper import NewsPaperRepository, NewsPaper
from .extractor import NewsPaperExtractor
from typing import List
from ..common.tools import print_exception,get_url
from bs4 import BeautifulSoup
import requests
from ..model.bcube import BcubeMD, BcubeMDRepository


class BCubeExtractor(NewsPaperExtractor):
    def __init__(self,repo:NewsPaperRepository, md_repo:BcubeMDRepository):
        super().__init__(repo)
        self._engine = "bCube"
        self._md_repo = md_repo

    def get_categories(self,np:NewsPaper)->BcubeMD:
        return None

    # TODO List of Articles
    def extract_one_category(self,np,cat)->List[str]:
        return None
    
    # TODO List of Articles
    def extract_one(self,np:NewsPaper)-> List[str]:
        print(f"\nextracting {np.short_name}")
        categories = self.get_categories(np)
        # Si no hay categorias, no es de este extractor
        if categories is None:
            return None

        self._md_repo.save(categories)
        
        print(f"  found {len(categories)} categories: {categories}")
        for cat in categories.found_cats:
            try:
                self.extract_one_category(np,cat)  
            except Exception as e:
                print_exception(e)
        
        return None # None means this newspaper is not from this extractor


class BCubePrensaIbericaExtractor(BCubeExtractor):
    def __init__(self,repo:NewsPaperRepository, md_repo:BcubeMDRepository):
        super().__init__(repo=repo,md_repo=md_repo)
        self._subengine = "PrensaIberica"
    
    def _extract_categories(self,np:NewsPaper, response:requests.Response,url:str)->BcubeMD:
        #html = response.content.decode("utf-8")
        ret = BcubeMD(ccaa=np.ccaa,short_name=np.short_name,
                        link_on_foot=None,
                        url_head_link=None,
                        url_head_og=None,
                        found_cats=[])
        if np.engine is None:
            print(f"  no engine for {np.short_name}")
            print(f" requested url: {url}")
            print(f" response url: {response.url}")
            # Primera proteccion contra sitios que no dan 404
            if response.url != url:
                print(f"    !404 Protection 1!")
                return None
                
        doc = BeautifulSoup(response.content, 'lxml')
        sections = doc.find_all('section')
        for s in sections:
            links  = s.find_all('a')
            for l in links:
                href= l['href']
                #print(f"  {href} -> {l['class']}")
                ret.found_cats.append(href.replace(np.real_url,"/"))
        if len(ret.found_cats)==0:
            return None
        return ret

    def get_categories(self,np:NewsPaper)->List[str]:
        url = np.real_url+"mapaweb/"
        response =get_url(url)
        if response.status_code == 499:
            url = np.real_url.replace("https://","https://www.")
            response =get_url(url+"mapaweb/")
            if response.status_code==200:
                np.real_url=url
        if response.status_code != 200: return None
        
        cats = self._extract_categories(np,response,url)
        return cats
