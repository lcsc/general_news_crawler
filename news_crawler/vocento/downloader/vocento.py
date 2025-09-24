from datetime import date, datetime
from bs4 import BeautifulSoup

from news_crawler.bcube.model.bcube import  BcubeCategory
from ...core.fetcher.extractor import NewsArticleReaderContext, NewsArticleReader, NewsArticleReader
from ...core.model.newspaper import NewsPaper, NewsArticle
from ...core.model.repos import CrawlerRepos

from typing import List,Dict
from ...common.tools import get_url, print_exception

from ...common.consts import ENGINE_ID_Vocento, SUBENGINE_ID_vc_v22

import bs4.element
import time

from datetime import datetime,timezone


import logging
LOG = logging.getLogger(__name__)

import urllib.parse

class VocentoArticleReaderContext(NewsArticleReaderContext):
    def __init__(self,news_paper:NewsPaper,category:BcubeCategory): # category:BcubeCategory
        super().__init__(news_paper)
        self.category=category
        self.last_page=1
        self.first_404=None
        self.page_size={}
        self.pagesHelper:Dict[int,Dict]={}

    

class VocentoArticleReader(NewsArticleReader):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)

    def get_date(self,txt:str)->datetime:
        # deberia ser el formato '%d %b. %Y %H:%M'
        # pero como no sabemos donde se ejcutara lo hacemos a mano
        parts = txt.split()
        year = None
        month = None
        day = None
        hour = None
        minute = None
        if len(parts)==3 or len(parts)==4:
            tDay= parts[0]
            tMonht = parts[1]
            tYear= parts[2]
            tHour = parts[3] if len(parts)==4 else None

            if tYear and tYear.isdigit() and len(tYear)==4:
                year = int(tYear)
            if  tDay and tDay.isdigit() and len(tDay)<=2:
                day = int(tDay)
            if tMonht.endswith('.'):
                month_str = tMonht.removesuffix('.').lower()
                month = None
                if month_str == "ene":
                    month = 1
                elif month_str == "feb":
                    month = 2
                elif month_str == "mar":
                    month = 3
                elif month_str == "abr":
                    month = 4
                elif month_str == "may":
                    month = 5
                elif month_str == "jun":
                    month = 6
                elif month_str == "jul":
                    month = 7
                elif month_str == "ago":
                    month = 8
                elif month_str == "sep":
                    month = 9
                elif month_str == "oct":
                    month = 10
                elif month_str == "nov":
                    month = 11
                elif month_str == "dic":
                    month = 12
            if tHour and len(tHour)==5 and tHour[2]==':':
                th = tHour.split(':')
                if th[0].isdigit() and len(th[0])<=2:
                    hour = int(th[0])
                if th[1].isdigit() and len(th[1])<=2:
                    minute = int(th[1])
        #print(f"  date parts: {day}-{month}-{year} {hour}:{minute}")
        if year is None or month is None or day is None:
            return None
        date = datetime(year,month,day,
                        hour=hour if hour is not None else 0,
                        minute=minute if minute is not None else 0,
                        tzinfo=timezone.utc)
        
        return date

    def _find_date(self,html:bs4.element.Tag)->(datetime | None):
        lp = html.find_all('p')
        for p in lp:
            txt = p.get_text().replace('\n',' ').strip()
            #print("p: ", txt)
            #print("date: ", self.get_date(txt))
            date = self.get_date(txt)
            if date is not None:
                return date
        return None
    
    def _get_title_url(self,html:bs4.element.Tag)->(str | None,str | None):
        la = html.find_all('a')
        for a in la:
            if a.has_attr('title') and a.has_attr('href'):
                return a.get('title'), a.get('href')
        return None,None
    
    def parse_article(self,html:bs4.element.Tag,context:VocentoArticleReaderContext)->(NewsArticle | None):

        # print("--- ARTICLE ---")
        #print(html.prettify())
        date = self._find_date(html)
        title, url = self._get_title_url(html)
        id:str = url.split('/')[-1] if url is not None else None
        if id is not None and id.endswith('.html'):
            id = id.removesuffix('.html')
        # print(f"  title: {title}")
        # print(f"  url: {url}")
        # print(f"  id: {id}")
        # print(f"  date: {date}")
        ret = self.createOrUpdateArticle(np=context.news_paper,
                                         article_id=id,
                                         engine_id=f"{ENGINE_ID_Vocento}-{SUBENGINE_ID_vc_v22}",
                                         title=title,
                                         url=url,
                                         date=date,
                                         engine_data=None,
                                         categories=[context.category.cat_name]
                                         )


        return ret

    def get_articles(self,context:VocentoArticleReaderContext,html:str)->List[NewsArticle]:
        vcReader:VocentoArticleReader = VocentoArticleReader(self.repos) # type: ignore

        doc = BeautifulSoup(html, 'lxml')
        articles:List[NewsArticle] = [] 
        items = doc.find_all('li')
        for it in items:
            try:
                article = vcReader.parse_article(it,context)
                if article is not None:
                    articles.append(article)
                    context.addArticle(article)

            except Exception as e:
                LOG.error(f"Error parsing article in {context.news_paper.short_name} {context.category.cat_name if context.category is not None else ''}")
                LOG.debug(e)
            #return None # Developement in progress stop here
                
        return articles

    def get_categories(self,page:str)->List[str]: # category:BcubeCategory
        doc = BeautifulSoup(page, 'lxml')
        h3 = doc.find_all('h3')
        cats = []
        for h in h3:
            txt  = h.get_text().strip().lower()
            if "mapa web" == txt:
                links = h.parent.find_all('a')
                for a in links:
                    href = a.get('href')
                    if href is not None and href.startswith('/'):
                        if href not in cats:
                            cats.append(href)   
                        else:
                            LOG.debug(f"  ignoring link {href} in mapa web")

        return cats


class VocentoDownloader():
    def __init__(self,reader:VocentoArticleReader):
        self._reader=reader
        pass

    def get_category_page(self,np:NewsPaper,context:VocentoArticleReaderContext,cat:BcubeCategory,page:int,date_range=None):
        
        base_url = np.real_url+"ajax/v22/archive?"
        params = {
                "type-crono": "archive-text",
                "page": page,
                "device": "desktop",
                "archive-text": "",
                "archive-date": "",
                "archive-day": "",
                "archive-month": "",
                "archive-year": "",
                "archive-startDay": "",
                "archive-startMonth": "",
                "archive-startYear": "",
                "archive-endDay": "",
                "archive-endMonth": "",
                "archive-endYear": "",
                "archive-format": "",
                "filter": "true",
                "section[]": "",
                "subsection[]": cat.cat_name[1:-1],
                "date": "",
                "order": "+fecha"
        }

        url = base_url + urllib.parse.urlencode(params, doseq=True)
        
        LOG.debug(f"  Downloading category page {page} from {url}")

        response =get_url(url)
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(url)
                count+=1
        
        if response.status_code==200:
            return response.content
        return None

    def get_mapa_web(self,news_paper:NewsPaper):
        
        url = news_paper.real_url+"mapa-web.html"
        LOG.debug(f"Downloading mapa web for {news_paper.short_name} from {url}")

        response =get_url(url)
        if response.status_code == 503: # este error puede ser puntual
            count =0
            while count < 5 and response.status_code==503:
                time.sleep(1) # reintentamos al segundo maximo 5
                response =get_url(url)
                count+=1
        
        if response.status_code==200:
            return response.content
        return None