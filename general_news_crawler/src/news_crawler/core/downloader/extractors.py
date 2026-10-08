import requests
from bs4 import BeautifulSoup
import json


from typing import Dict, List
from news_crawler.core.model import NewsPaper, NewsArticle

import logging
from news_crawler.core.model.repos import CrawlerRepos
from news_crawler.common.consts import ENGINE_ID_bCube

LOG:logging.Logger=logging.getLogger(__name__)

import ast

def build_article_data(headline: str, body: str, date: str, url: str, article: NewsArticle, a_type="NewsArticle") -> Dict:
    """
    Builds a dictionary with the article data.
    """
    if headline is None or len(headline) == 0:
            LOG.warning(f"No headline found for article {article.article_id}")
            return None
    if body is None or len(body) == 0:
        LOG.warning(f"No body content found for article {article.article_id}")
        return None
    if date is None:
        LOG.warning(f"No date found for article {article.article_id}")
        return None
    if url is None:
        LOG.warning(f"No URL found for article {article.article_id}")
        return None
    return {"NewsArticle":{"@type":a_type,
                            "headline":headline,
                            "articleBody":body,
                            "datePublished":date,
                            "mainEntityOfPage":url}}

class ArticleExtractor():
    def __init__(self, repos:CrawlerRepos):
        self.repos = repos
        pass
    def extract(self, paper:NewsPaper, article:NewsArticle, html:requests.Response) -> Dict:
        """
        Extracts data from the article HTML.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class JsonArticleExtractor(ArticleExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        pass
    
    def _get_type_id(self,type:str, ret:Dict):
        if type not in ret:
            return ret
        i= 0
        while f"{type}_{i}" in ret:
            i += 1
        return f"{type}_{i}"
    
    def extract(self, paper:NewsPaper, article:NewsArticle, html:requests.Response) -> Dict:
        if html is None:
            return None
        doc = BeautifulSoup(html.content, 'lxml')
        scripts = doc.find_all("script", {"type": "application/ld+json"})
        if scripts is None or len(scripts) == 0:
            LOG.warning(f"No JSON-LD data found for article {article.article_id}")
            return None
        LOG.debug(f"Found {len(scripts)} JSON-LD scripts for article {article.article_id}")
        ret = {}

        for data in scripts:
            try:    
                json_data = json.loads(data.string)
                if isinstance(json_data, dict):
                    json_data = [json_data]  # Convert single dict to list for consistency
                for item in json_data:
                    type = item.get("@type", None)
                    if type is None:
                        LOG.warning(f"No JSON-LD type found for article {article.article_id}.")
                        continue
                    if type in ret:
                        LOG.warning(f"Duplicate JSON-LD type {type} found for article {article.article_id}.")
                        type = self._get_type_id(type, ret)
                        LOG.info(f"Using JSON-LD type {type} for article {article.article_id}.")
                    ret[type] = item
                
            except json.JSONDecodeError as e:
                LOG.error(f"Error decoding JSON-LD data for article {article.article_id}: {e}")
        
        return ret if len(ret) > 0 else None
class WpListContentExtractor(ArticleExtractor):
    def __init__(self, repos:CrawlerRepos):
        super().__init__(repos)
        pass
    
    def _extract_rendered(self, wpPost:Dict, key:str) -> str:
        """
        Extracts the rendered content from the WordPress post.
        """
        if key not in wpPost:
            return None
        if "rendered" not in wpPost[key]:
            LOG.error(f"No rendered content found for {key} in {wpPost.keys()}")
            return None
        rendered = wpPost[key]["rendered"]
        if not isinstance(rendered, str):
            LOG.error(f"Rendered content for {key} is not a string: {type(rendered)}")
            return None
        
        doc = BeautifulSoup(rendered, 'lxml')
        if doc is None:
            LOG.error(f"Failed to parse rendered content for {key} in {wpPost.keys()}")
            return None
        text = doc.text
        #LOG.debug(f"Extracted text for {key}: {text}")

        return text

    def extract(self,paper:NewsPaper,  article:NewsArticle, html:requests.Response) -> Dict:
       content= self.repos.read_file(article.raw_data, "list")
       LOG.debug(f"Extracting content from {article.raw_data} for article {article.article_id}")

       if content is None:
            return None
       headline = None
       body = None
       date = None
       url = None
       try:
            if content.startswith("{'"):
                json_data = ast.literal_eval(content)
            else:
                json_data = json.loads(content)
            
            #     LOG.debug(f"Content is in single quotes, converting to double quotes for article {article.article_id}")
            #     content=content.replace("'","\"")
            # if ": True" in content:
            #     LOG.debug(f"Content has : True, replacing with : true for article {article.article_id}")
            #     content=content.replace(": True", ": true")
            # if ": False" in content:
            #     LOG.debug(f"Content has : False, replacing with : false for article {article.article_id}")
            #     content=content.replace(": False", ": false")
            # if ": None" in content:
            #     LOG.debug(f"Content has : None, replacing with : null for article {article.article_id}")
            #     content=content.replace(": None", ": null")

            # LOG.debug(f"Decoding WP data for article {article.article_id}\n\n{content}\n\n")
            
            # json_data = json.loads(content)
            headline= self._extract_rendered(json_data, "title")
            body = self._extract_rendered(json_data, "content")
            date = json_data.get("date", None)
            url = json_data.get("link", None)

       except Exception as e:
            LOG.error(f"Error decoding WP data for article {article.article_id}: {e}")
            return None
       return build_article_data(headline, body, date, url,article)

brandedContentFoundPapers=["elperiodicoextremadura","lacronicabadajoz"]

class BcubeBrandedContent(ArticleExtractor):
    def __init__(self, repos:CrawlerRepos):
        super().__init__(repos)
        pass

    def is_branded_content(self, doc:BeautifulSoup) -> bool:
        scripts = doc.find_all("script")
        for script in scripts:
            if script.string and "branded content" in script.string:
                LOG.debug("Branded content found in script tag.")
                return True
        return False
    
    def extract(self, paper:NewsPaper, article:NewsArticle, html:requests.Response) -> Dict:
        LOG.debug(f"Extracting branded content for article {article.article_id} for paper {paper.name}")
        if  not paper.engine or paper.engine.engine != ENGINE_ID_bCube:
            LOG.debug(f"Paper {paper.name} is not a {ENGINE_ID_bCube} paper, skipping branded content extraction. ({paper.engine})")
            return None
        if paper.short_name not in brandedContentFoundPapers:
            LOG.debug(f"Paper {paper.short_name} is not in the list of branded content papers, skipping extraction.")
            return None
        if html is None:
            return None


        doc = BeautifulSoup(html.content, 'lxml')

        if not self.is_branded_content(doc):
            LOG.debug(f"No \"branded content\" found in article {article.article_id} for paper {paper.name}.")
            return None

        headline = doc.find("title").text if doc.find("title") else article.article_headline
        
        body = doc.find("div", {"class": "inner"}).text if doc.find("div", {"class": "inner"}) else None
        
        if body is None:
            body=doc.find("div", {"class": "content-inner"}).text if doc.find("div", {"class": "content-inner"}) else None
        
        if body is None:
            body = doc.find("article", {"class": "post"}).text if doc.find("article", {"class": "post"}) else None

        if body is None:
            body = doc.find("main", {"class": "main-root"}).text if doc.find("main", {"class": "main-root"}) else None

        if body is None:
            body=doc.find("div", {"class": "project-info"}).text if doc.find("div", {"class": "project-info"}) else None

        # <div id="blog-page"
        if body is None:
            body=doc.find("div", {"id": "blog-page"}).text if doc.find("div", {"id": "blog-page"}) else None
        # <main   
        if body is None:
            body=doc.find("main").text if doc.find("main") else None




        date = article.date
        url = article.article_url

        return build_article_data(headline, body, date, url,article)
    
class ArticleContent(ArticleExtractor):
    def __init__(self, repos:CrawlerRepos):
        super().__init__(repos)
        pass

    def extract(self, paper:NewsPaper, article:NewsArticle, html:requests.Response) -> Dict:

        doc = BeautifulSoup(html.content, 'lxml')

        body = doc.find("article", {"id": "article"}).text if doc.find("article", {"id": "article"}) else None

        headline = doc.find("title").text if doc.find("title") else article.article_headline
        date = article.date
        url = article.article_url

        return build_article_data(headline, body, date, url,article)