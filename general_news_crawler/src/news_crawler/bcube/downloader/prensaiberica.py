from ...core.model.newspaper import NewsArticle
from ...common.tools import get_url
import requests
from .bcube import BcubeArticleReaderContext
from ...core.model.repos import CrawlerRepos
from datetime import datetime,timezone
from ...common.consts import ENGINE_ID_bCube,SUBENGINE_ID_bc_PrensaIberica
from .bcube import BcubeArticleReader
 
import sys
import time

import logging

LOG = logging.getLogger(__name__)

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

    def _extract_date_from_url_regex(self, url:str)->datetime:
        """
        Extracts the date from the URL using a regex pattern.
        The expected format is .../YYYY/MM/DD/....
        """
        import re
        match = re.search(r'(/\d{4}/\d{2}/\d{2}/)', url)
        if match:
            date_str = match.group(1)
            date_str = date_str[1:-1]  # Remove leading and trailing slashes
            date_str = date_str.replace("/", "-")  # Replace slashes with dashes
            date = datetime.fromisoformat(date_str)

            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            LOG.debug(f"Extracted date from URL: {date.isoformat()}")
            return date.isoformat()
        return None        

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
            LOG.info("No title found in article, using empty title")
            print("****** Failed *****")
            print(tag)
            print(data)
            print("****** Failed *****")
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
            LOG.debug("article without any date")
            try:
                url = data["data-url"]
                date_str = url.removeprefix(np.real_url)
                date_str= date_str.removeprefix(cat.cat_name[1:])
                date_str = date_str[0:10]
                date = date_str.replace("/","-")
                date= datetime.fromisoformat(date) 
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                date = date.isoformat()
            except Exception as e:
                LOG.debug(f"Error parsing date {date_str} of {url}, trying regex")
                LOG.debug(e)
                date = self._extract_date_from_url_regex(data["data-url"])
        if date is None:
            LOG.debug("No date Found")
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
        t_start = datetime.now()
        response =get_url(np.real_url+"webapi/module-pagination/?url="+cat.cat_name+"&page="+str(page))
        
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(np.real_url+"webapi/module-pagination/?url="+cat.cat_name+"&page="+str(page))
                count+=1
        t_download = datetime.now()
        
        if response.status_code == 404:
            if context.first_404 is None:
                context.first_404 = page
            else:
                context.first_404 = min(context.first_404,page)
            return response

        if response.status_code==200:
            json = response.json()
            articles =self._reader.extract_list(context,json)
            context.lastFound=articles
            if articles is None:
                return response
            if page > context.last_page:
                context.last_page=page
            context.page_size[page]=len(articles)
        t_read_save =datetime.now()

        LOG.debug(f"Descarga: {t_download-t_start} Process: {t_read_save - t_download}")
            
        return response