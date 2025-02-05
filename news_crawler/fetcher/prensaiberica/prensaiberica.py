from ...model.newspaper import NewsPaperRepository, NewsPaper
from typing import List
from ...common.tools import get_url
from bs4 import BeautifulSoup
import requests
from ...model.bcube import BcubePiMd
from .pi_tools import pi_has_link_on_footer,pi_get_head_link_canonical,pi_get_head_meta_ogurl
from ..bcube import BCubeExtractor
from ...model.repos import CrawlerRepos

class BCubePrensaIbericaExtractor(BCubeExtractor):
    def __init__(self,repos:CrawlerRepos, ):
        super().__init__(repos=repos)
        self._subengine = "PrensaIberica"
    
    
    def _extractMD(self,doc:BeautifulSoup,ret:BcubePiMd):
        ret.link_on_foot=pi_has_link_on_footer(doc)
        ret.url_head_link=pi_get_head_link_canonical(doc)
        ret.url_head_og=pi_get_head_meta_ogurl(doc)

    def _getMetada(self, ccaa:str,short_name:str)->BcubePiMd:
        ret = self._np_repos.bCubePiMd.find_one_by({"ccaa":ccaa,"short_name":short_name})
        if ret is None:
            ret = BcubePiMd(ccaa=ccaa,short_name=short_name,
                        link_on_foot=None,
                        url_head_link=None,
                        url_head_og=None,
                        found_cats=[])
        return ret   

    def _extract_categories(self,np:NewsPaper, response:requests.Response,url:str)->BcubePiMd:
        #html = response.content.decode("utf-8")
        ret = self._getMetada(ccaa=np.ccaa,short_name=np.short_name)

        if np.engine is None:
            print(f"  no engine for {np.short_name}")
            print(f" requested url: {url}")
            print(f" response url: {response.url}")
            # Primera proteccion contra sitios que no dan 404
            if response.url != url:
                print(f"    !404 Protection 1!")
                return None
                
        doc = BeautifulSoup(response.content, 'lxml')
        #if np.engine is None:
        self._extractMD(doc,ret)

        sections = doc.find_all('section')
        for s in sections:
            links  = s.find_all('a')
            for l in links:
                href= l['href']
                #print(f"  {href} -> {l['class']}")
                ret.found_cats.append(href.replace(np.real_url,"/"))
        
        if ret.link_on_foot: return ret
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
