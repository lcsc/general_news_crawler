import multiprocessing.synchronize
from .common import CommonArgs, GeneralOptions, CommonCmd
from .multiprocess import NewsWorker, launchMP_Workers
from typing import Dict, List
from datetime import datetime
import multiprocessing
import logging
from news_crawler.core.downloader import DownloadNewsJob, GeneralDownloader

LOG:logging.Logger=logging.getLogger(__name__)

class DownloadNewsArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,year:int,month:int,day:int, workers:int):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self.year=year
        self.month=month
        self.day=day
        self.workers=workers
        #self._bfillers:Dict[str,BackFiller]




def doDownloadNewsMp(data):
    name, taks = data
    downloader=GeneralDownloader(name, taks)
    downloader.donwload()



class DownloadWorker(NewsWorker):
    def __init__(self, name:str, args:List):
        super().__init__(name)
        self.args = args

    def getTarget(self):
        return doDownloadNewsMp

    def getArgs(self):
        return (self.name,self.args)

class DownloadNewsCmd(CommonCmd):
    def __init__(self, general:GeneralOptions, args:DownloadNewsArgs):
        super().__init__(general, args)
        self.args = args

    def downloadNews(self):
        LOG.info(f"Starting download for {self.args.year}-{self.args.month}-{self.args.day} with {self.args.workers} workers")
        
        workers = []
        tasks = [DownloadNewsJob("Aragon"), DownloadNewsJob("BcubePi"), DownloadNewsJob("Wp")]
        for i in range(self.args.workers):
            worker = DownloadWorker(f"DownloadWorker-{i}", tasks)
            workers.append(worker)

        launchMP_Workers(workers)

        
    def _downloadNews(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterArticles()
        LOG.info(f"Query to Mongo: {basic_filter}") 
        articles = repos.articles.find_by(basic_filter)
        articles = [article for article in articles if article.article_data is None]
        LOG.info(f"Found {len(articles)} articles to download")
        # Implement the logic to download news based on the provided arguments
        pass