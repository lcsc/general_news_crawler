from ....core.model.newspaper import NewsPaper, NewsArticle
from typing import List
from ....common.tools import get_url
from bs4 import BeautifulSoup
import requests
from ...model.prensaiberica import BcubePiMd
from ...tools.pi_tools import pi_has_link_on_footer,pi_get_head_link_canonical,pi_get_head_meta_ogurl
from ..bcube import BCubeExtractor,BcubeArticleReaderContext
from ....core.model.repos import CrawlerRepos
from ...model.bcube import BcubeCategory
from datetime import datetime
from ....common.consts import ENGINE_ID_bCube,SUBENGINE_ID_bc_PrensaIberica
import sys
import time

from ...downloader.prensaiberica import BcubePiArticleReader,BcubePiDownloader


class BCubePrensaIbericaExtractor(BCubeExtractor):
    def __init__(self,repos:CrawlerRepos ):
        super().__init__(repos=repos)
        self._subengine = SUBENGINE_ID_bc_PrensaIberica
        #self._reader:BcubePiArticleReader=BcubePiArticleReader(repos)
        self._downloader=BcubePiDownloader(BcubePiArticleReader(repos))
    
    
    def _extractMD(self,doc:BeautifulSoup,ret:BcubePiMd):
        ret.link_on_foot=pi_has_link_on_footer(doc)
        ret.url_head_link=pi_get_head_link_canonical(doc)
        ret.url_head_og=pi_get_head_meta_ogurl(doc)
        ret.found_cats=[]

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
                if not hasattr(l,'href'):continue
                href= l['href']
                #print(f"  {href} -> {np.real_url}")
                cat_name= href.replace(np.real_url,"/")
                ret.found_cats.append(cat_name)
        
        self._np_repos.bCubePiMd.save(ret) #Este repo es nuestro, conviene guardarlo
        if len(ret.found_cats)==0:
            return None
        
        if ret.link_on_foot: #Condiciones conocidas de que son de PI
            return ret
        
        return None

    def _convert_categories(self,np:NewsPaper,cats:BcubePiMd)->list[BcubeCategory]:
        if cats is None or len(cats.found_cats)==0:
            return None
        ret = []
        for cat in cats.found_cats:
            cat_data = self._find_category(np.ccaa,np.short_name,cat)
            if cat_data is None:
                cat_data=BcubeCategory(
                    id=None,
                    ccaa=np.ccaa,
                    short_name=np.short_name,
                    cat_name=cat,
                    cat_url=np.real_url[:-1]+cat,
                    first_article=None,
                    first_month=None
                )
            else:
                cat_data.cat_url=np.real_url[:-1]+cat #actualizamos la url por si acaso
            ret.append(cat_data)
        return ret

    def get_categories(self,np:NewsPaper)->list[BcubeCategory]:
        url = np.real_url+"mapaweb/"
        response =get_url(url)
        if response.status_code == 499:
            url = np.real_url.replace("https://","https://www.")
            response =get_url(url+"mapaweb/")
            if response.status_code==200:
                np.real_url=url
        if response.status_code != 200: return None
        
        cats = self._extract_categories(np,response,url)
        if cats is not None:
            cats =self._convert_categories(np,cats=cats)
        return cats
    



    def extract_one_category(self,np:NewsPaper,cat:BcubeCategory)->List[NewsArticle]:
        print(f"  Extracting {cat.cat_name}")
        context = BcubeArticleReaderContext(np,cat)
        tope=1
        n=1
        # try with page=1
        response = self._downloader.get_url_cat(context,1)
        if response.status_code!=200:
            #some pages gives error on page 1, try page2
            response =self._downloader.get_url_cat(context,2)
        if response.status_code != 200:
            return None

        while response.status_code==200:
            tope*=10
            response = self._downloader.get_url_cat(context,tope)

        while response.status_code == 404:
            tmp = int(tope/2)
            response = self._downloader.get_url_cat(context,tmp)

            if(response.status_code==404): tope=tmp
            else: n = tmp
        
        diff = tope - n
        while diff > 1:
            tmp = n + int(diff/2)
            if tmp==n: tmp +=1
            response = self._downloader.get_url_cat(context,tmp)

            if(response.status_code==404): tope=tmp
            else: n = tmp
            diff = tope - n
        context.last_page=n
        print(f"  {context.category.cat_name}: {context.page_size}")
        if n>2: # En caso contrario no tenemos suficiente informacion.
            if not (n-1) in context.page_size:
                response = self._downloader.get_url_cat(context,n-1)
                if response.status_code!=200:
                    print("ERROR?????")
                print(f"  {context.category.cat_name}: {context.page_size}")
            page_size=context.page_size[n-1]
            print (f"   PageSize: {page_size}")
            context.category.n_articulos=(n-1)*page_size+context.page_size[n]
            print (f"   num_arti: {context.category.n_articulos}")
        
        sys.stdout.flush() #cada vez que terminemos una cat, forzamos flush
        return context.getListArticles()

