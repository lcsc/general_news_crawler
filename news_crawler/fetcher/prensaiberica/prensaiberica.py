from ...model.newspaper import NewsPaper, NewsArticle
from typing import List
from ...common.tools import get_url
from bs4 import BeautifulSoup
import requests
from ...model.bcube.prensaiberica import BcubePiMd
from .pi_tools import pi_has_link_on_footer,pi_get_head_link_canonical,pi_get_head_meta_ogurl
from ..bcube import BCubeExtractor,BcubeArticleReaderContext, BcubeArticleReader
from ...model.repos import CrawlerRepos
from ...model.bcube.bcube import BcubeCategory

class BcubePiArticleReader(BcubeArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def _guess_id(self, data:dict)->str:
        if "data-content-id" in data:
            return data["data-content-id"]
        url:str = None
        if "data-url" in data:
            url = data["data-url"]
        else:
            url = data["itemid"]
        url = url.split("-")
        id:str = url[-1]
        id=id.removesuffix(".html")
        return id
        

    def _extract_list_one(self,context:BcubeArticleReaderContext,object:any)->NewsArticle:
        tag = object
        np = context.news_paper
        cat = context.category
        #print(tag)
        meta = tag.find_all('meta')
        date = None
        dateM = None
        dateU = None
        
        data={}
        for m in meta:
            if(m['itemprop']=='mainEntityOfPage'):
                data["itemid"]= m['itemid']
                continue
            elif hasattr(m,"content"):
                data[m['itemprop']]=m['content']

        if "itemid" not in data:
            link = tag.find("a",attrs={"title":True})
            if link is None:
                print("****** Failed *****")
                print(tag)
                print(data)
                print("****** Failed *****")
                return None
            data["itemid"]=link["href"]
            data["title"]=link["title"]

        data_url = tag.find_all(attrs={"data-url":True})
        if data_url is not None and len(data_url)==1:
            data["data-url"]=data_url[0]["data-url"]
            data["title"] = data_url[0]["title"]
        else:
            data["data-url"]=data["itemid"]
            


        if "title" not in data:
            title_el = tag.find(attrs={"title":True})
            if title_el is not None:
                data["title"]=title_el["title"]
        if "title" not in data:
            data["title"]="" # TODO: return None?

        data_id = tag.find_all(attrs={"data-content-id":True})
        if data_id is not None and len(data_id)==1:
            data["data-content-id"]=data_id[0]["data-content-id"]

        #print(data)

        if 'datePublished' in data:
            date = data['datePublished']
        if 'dateModified' in data:
            dateM = data['dateModified']
        if 'uploadDate' in data:
            dateU = data['uploadDate']
    
        
        if date is None and dateM is not None:
            date = dateM
        if date is None and dateU is not None:
            date = dateU
        if date is None:
            print("article without any date")
            return None
        
        ret = None
        try:
            article_id  =self._guess_id(data)
            ret = self.repos.articles.find_one_by({"np_ccaa":np.ccaa,
                                                       "np_name":np.short_name,
                                                       "article_id":article_id,
                                                       })
            if ret is None:
                ret = NewsArticle(id=None,
                          np_ccaa=np.ccaa,
                          np_name=np.short_name,
                          article_id=article_id,
                )
            
            ret.article_headline=data["title"],
            ret.article_url=data["data-url"],
            ret.date= date,
            ret.engine_id="bCube-PrensaIberica",
            ret.engine_data=data

        except Exception as e:
            print("****** Failed *****")
            print(e)
            print(tag)
            print(data)
            print("****** Failed *****")

        return ret

class BCubePrensaIbericaExtractor(BCubeExtractor):
    def __init__(self,repos:CrawlerRepos ):
        super().__init__(repos=repos)
        self._subengine = "PrensaIberica"
        self._reader:BcubePiArticleReader=BcubePiArticleReader(repos)
    
    
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
    

    def _get_url_cat(self,context:BcubeArticleReaderContext,page:int)->requests.Response:
        np = context.news_paper
        cat = context.category

        response =get_url(np.real_url+"webapi/module-pagination/?url="+cat.cat_name+"&page="+str(page))

        if response.status_code==200:
            json = response.json()
            articles =self._reader.extract_list(context,json)
            if articles is None:
                return response
            for a in articles:
                a.engine_data["category"]=cat.cat_name
                
        return response

    def extract_one_category(self,np:NewsPaper,cat:BcubeCategory)->List[NewsArticle]:
        print(f"  Extracting {cat.cat_name}")
        context = BcubeArticleReaderContext(np,cat)
        tope=1
        n=1
        # try with page=1
        response = self._get_url_cat(context,1)
        if response.status_code!=200:
            #some pages gives error on page 1, try page2
            response =self._get_url_cat(context,2)
        if response.status_code != 200:
            return None
        

        return list(context.articles.values())


