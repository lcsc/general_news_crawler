import logging
import os
import time
import random

from typing import Dict, List
from datetime import datetime
from news_crawler.core.model import NewsPaper, NewsArticle

import multiprocessing
import ctypes

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
    def __init__(self, name:str, task:List[DownloadNewsJob]):
        self.name = name
        self.tasks = task
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
        
        article = job.downloaded_articles[job.data["next_article"]]
        LOG.info(f"Worker {name} is downloading article {article.article_id} for {job.news_paper.name}")
        # Here you would implement the actual downloading logic
        time.sleep(random.uniform(0.2, 0.6))  # Simulate download time
        LOG.info(f"Downloaded article {article.article_id} for {job.news_paper.name}")
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

                if job.sync["last_downloaded"] is None or (datetime.now() - job.sync["last_downloaded"]).total_seconds() > 35:  # If the job was not downloaded in the last 35s
                    job.sync["owner"] = name
                    LOG.debug(f"Selected task {job.news_paper.name} for {job.sync['owner']}")
                    return job
        return None

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
            
            job = self.select_one_task(tasks,name)
            #LOG.debug(f"Selected job: {job}")
            if job is None:
                #LOG.debug(f"No more tasks available for {name}, waiting")
                time.sleep(0.5+random.random())  # Wait for a while before checking again
                continue
            if job.sync["owner"] != name:
                #LOG.debug(f"task {job.news_paper.name} is not assigned to {name}, waiting")
                time.sleep(0.5+random.random())  # Wait for a while before checking again
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
            
                 