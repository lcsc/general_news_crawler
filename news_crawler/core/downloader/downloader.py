import logging
import os
import time
import random

from typing import List
from datetime import datetime
from news_crawler.core.model import NewsPaper, NewsArticle
from .extractors import JsonArticleExtractor, ArticleExtractor, WpListContentExtractor, BcubeBrandedContent

from news_crawler.common.tools import get_url

from news_crawler.core.model.repos import CrawlerRepos

LOG:logging.Logger=logging.getLogger(__name__)


class DownloadNewsJob():
    def __init__(self, np:NewsPaper, articles:List[NewsArticle],lock, manager):
        # Sync variables
        self.lock = lock
        self.sync = manager.dict()
#        self.sync = {}
        self.sync["owner"] = None
        self.sync["last_downloaded"] = None
        
        
        # Job specific variables
        self.data = manager.dict()
        self.data["done"] = False
        self.data["next_article"] = 0  # Index of the next article to download

        self.news_paper:NewsPaper = np
        self.downloaded_articles:List[NewsArticle] = articles

        pass

        
class GeneralDownloader():
    def __init__(self, name:str, task:List[DownloadNewsJob], repos:CrawlerRepos,
                  min_np_Delay_s=13, report_interval_m=10,no_task_wait_s=0.5):
        
        self.name = name
        self.tasks = task
        self.extractor: List[ArticleExtractor] = [JsonArticleExtractor(repos),
                                                  WpListContentExtractor(repos),
                                                  BcubeBrandedContent(repos)]
        self.repos = repos
        self.last_report = datetime.now()
        self.min_np_Delay_s = min_np_Delay_s  # Minimum delay between downloads for the same news paper
        self.report_interval_m = report_interval_m  # Interval to report statistics in minutes
        self.no_task_wait_s = no_task_wait_s  # Time to wait when no tasks are available
        pass


    def check_job_done(self,job:DownloadNewsJob)->bool:
        """
        Checks if the job is done.
        """
        if len(job.downloaded_articles)==job.data["next_article"] :
            return True
        return False

    def download_one(self,job:DownloadNewsJob, name:str):
        """
        Downloads the news for the given job.
        This function should implement the actual downloading logic.
        """
        if job.downloaded_articles is None or len(job.downloaded_articles) == 0:
            LOG.warning(f"No articles to download for {job.news_paper.name}")
            return
        
        article:NewsArticle = job.downloaded_articles[job.data["next_article"]]
        paper = job.news_paper
        
        #puesto solamente para probar el crawler
        # while "/videos/" in article.article_url:
        #     LOG.warning(f"Skipping video article {article.article_id} for {job.news_paper.name}")
        #     job.data["next_article"] += 1
        #     if job.data["next_article"] >= len(job.downloaded_articles):
        #         LOG.info(f"All articles downloaded for {job.news_paper.name}")
        #         return
        #     article = job.downloaded_articles[job.data["next_article"]]

        LOG.info(f"Worker {name} is downloading article {article.article_id} for {job.news_paper.name}")
        
        try:

            response = get_url(article.article_url)
            if response.status_code != 200:
                LOG.error(f"Error downloading article {article.article_id} for {job.news_paper.name}: {response.status_code}")
                return
            
            if response.headers.get('Content-Type', '')=='application/pdf' or \
               response.headers.get('content-type', '')=='application/pdf':
                LOG.info(f"Article {article.article_id} is a PDF, saving directly")
                path = article.raw_data.replace(".list_raw", ".pdf")
                self.repos.save_file(path, response.content,'article',article.date)
                article.article_data = path
                self.repos.articles.save(article)
                LOG.info(f"Saved article {article.article_id} for {job.news_paper.name}")
                return
            for extractor in self.extractor:
                data = extractor.extract(paper, article, response)
                if data is not None:
                    #article.data = data
                    LOG.info(f"Extracted data for article {article.article_id} for {job.news_paper.name}")
                    #path =f"{np_base_path(context.news_paper)}{cat}{article.article_id}.list_raw"
                    
                    path = article.raw_data.replace(".list_raw", ".json")
                    LOG.info(f"Saving article {article.article_id} for {job.news_paper.name} to {path}")

                    self.repos.save_file(path, str(data),'article',article.date)
                    article.article_data = path
                    self.repos.articles.save(article)
                    LOG.info(f"Saved article {article.article_id} for {job.news_paper.name}")
                    break
        except Exception as e:
            LOG.error(f"Error downloading article {article.article_id} for {job.news_paper.name}: {e}")
        finally:
            # usamos el finally para asegurarnos de que se marca como descargado
            LOG.info(f"End Downloaded article {article.article_id} for {job.news_paper.name} (en finally)")
            with job.lock:
                job.data["next_article"] += 1

        

    def select_one_task(self,tasks:List[DownloadNewsJob], name:str)-> DownloadNewsJob:
        """
        Selects one task from the list of news papers.
        This is a simple selection strategy, you can implement more complex strategies if needed.
        """
        for job in tasks:
            with job.lock:
                if job.data["done"]: continue

                if job.sync["owner"] is not None: continue

                if job.sync["last_downloaded"] is None or (datetime.now() - job.sync["last_downloaded"]).total_seconds() > self.min_np_Delay_s:  # If the job was not downloaded in the last min_np_Delay_s seconds
                    job.sync["owner"] = name
                    LOG.debug(f"Selected task {job.news_paper.name} for {job.sync['owner']}")
                    return job
        return None

    def print_stats(self):
        """
        Prints the statistics of the downloader.
        """
        if (datetime.now() - self.last_report).total_seconds() < (60*self.report_interval_m):
            return
        LOG.info(f"Downloader {self.name} statistics:")
        total_articles = 0
        total_done = 0
        for job in self.tasks:
            #no usamos lock porque es solo lectura y estadisticas
            total_articles += len(job.downloaded_articles)
            total_done += job.data["next_article"] -1 # -1 because next_article is the index of the next article to download
        LOG.info(f"Progress: {total_done}/{total_articles} articles downloaded {total_done/total_articles*100:.2f}%")        
        self.last_report = datetime.now()

    def donwload(self):
        name= self.name
        tasks = self.tasks

        LOG.info("Starting Download News Multiprocessing")
        LOG.debug(f"Worker Name: {name}")
        LOG.debug(f"Tasks: {tasks}")
        if tasks is None or len(tasks) == 0:
            LOG.info("No tasks available, exiting")
            return
        while True:
            if all(job.data["done"] for job in tasks):
                LOG.info("All jobs are done, exiting")
                break
            self.print_stats()
            
            job = self.select_one_task(tasks,name)
            #LOG.debug(f"Selected job: {job}")
            if job is None:
                #LOG.debug(f"No more tasks available for {name}, waiting")
                time.sleep(self.no_task_wait_s+random.random())  # Wait for a while before checking again
                continue
            if job.sync["owner"] != name:
                #LOG.debug(f"task {job.news_paper.name} is not assigned to {name}, waiting")
                time.sleep(self.no_task_wait_s+random.random())  # Wait for a while before checking again
                continue
            LOG.info(f"Worker {name} is processing task for {job.news_paper.name}")
            try:
                self.download_one(job,name)
                with job.lock:
                    job.sync["last_downloaded"] = datetime.now()
                    job.data["done"] = self.check_job_done(job)
                    job.sync["owner"] = None

            except Exception as e:
                LOG.error(f"Error while downloading news for {job.news_paper.name}: {e}")
            
                 