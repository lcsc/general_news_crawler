from ...core.model.newspaper import NewsArticle
from ...common.tools import get_url
import requests
from .bcube import BcubeArticleReaderContext
from ...core.model.repos import CrawlerRepos
from datetime import datetime
from ...common.consts import ENGINE_ID_bCube,SUBENGINE_ID_bc_PrensaIberica
from .bcube import BcubeArticleReader
 
import sys
import time

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
        date = datetime.fromisoformat(date)
        data["category"]=context.category.cat_name
        ret = None
        try:
            article_id  =self._guess_id(data)
            ret = self.createOrUpdateArticle(np=np,
                                         article_id=article_id,
                                         engine_id=f"{ENGINE_ID_bCube}-{SUBENGINE_ID_bc_PrensaIberica}",
                                         title=data["title"],
                                         url=data["data-url"],
                                         date=date,
                                         engine_data=data,
                                         categories=[context.category.cat_name]
                                         )


        except Exception as e:
            print("****** Failed *****")
            print(e)
            print(tag)
            print(data)
            print("****** Failed *****")

        return ret
    
class BcubePiDownloader():
    def __init__(self,reader:BcubePiArticleReader):
        self._reader:BcubePiArticleReader=reader
        pass

    def get_url_cat(self,context:BcubeArticleReaderContext,page:int)->requests.Response:
        np = context.news_paper
        cat = context.category

        response =get_url(np.real_url+"webapi/module-pagination/?url="+cat.cat_name+"&page="+str(page))
        
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(np.real_url+"webapi/module-pagination/?url="+cat.cat_name+"&page="+str(page))
                count+=1
        
    
        if response.status_code==200:
            json = response.json()
            articles =self._reader.extract_list(context,json)
            context.lastFound=articles
            if articles is None:
                return response
            if page > context.last_page:
                context.last_page=page
            context.page_size[page]=len(articles)
            
            
        return response