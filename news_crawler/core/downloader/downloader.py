import logging
import os
import time
import random

from typing import Dict, List
from datetime import datetime
import multiprocessing

LOG:logging.Logger=logging.getLogger(__name__)

class DownloadNewsJob():
    def __init__(self, np:str ):
        # Sync variables
        self.owner:str = None
        self.last_downloaded:datetime = None
        self.lock:multiprocessing.synchronize.Lock = multiprocessing.Lock()
        
        # Job specific variables
        self.news_paper:str = np
        self.downloaded_articles:List[str] = []
        self.done=False
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
        if len(job.downloaded_articles)==2 :
            return True
        return False

    def download_one(self,job:DownloadNewsJob, name:str):
        """
        Downloads the news for the given job.
        This function should implement the actual downloading logic.
        """
        LOG.info(f"Worker {name} is downloading one article for {job.news_paper}")
        # Simulate download
        time.sleep(random.random() * 2)  # Simulate some download time
        job.downloaded_articles.append(f"Downloaded articles for {job.news_paper} by {name}")

    def select_one_task(self,tasks:List[DownloadNewsJob], name:str)-> DownloadNewsJob:
        """
        Selects one task from the list of news papers.
        This is a simple selection strategy, you can implement more complex strategies if needed.
        """
        for job in tasks:
            with job.lock:
                if job.done: continue
                if job.owner is not None: continue
                if job.last_downloaded is None or (datetime.now() - job.last_downloaded).total_seconds() > 35:  # If the job was not downloaded in the last 35s
                    job.owner = name
                    LOG.debug(f"Selected task {job.news_paper} for {job.owner}")
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
            job = self.select_one_task(tasks,name)
            if job is None or job.owner is not name:
                LOG.info(f"No more tasks available for {name}, waiting")
                time.sleep(0.5+random.random())  # Wait for a while before checking again
                continue
            LOG.info(f"Worker {name} is processing task for {job.news_paper}")
            try:
                self.download_one(job,name)
                with job.lock:
                    job.last_downloaded = datetime.now()
                    job.done = self.check_job_done(job)
                    job.owner = None

            except Exception as e:
                LOG.error(f"Error while downloading news for {job.news_paper}: {e}")
            
            if all(job.done for job in tasks):
                LOG.info("All jobs are done, exiting")
                break        