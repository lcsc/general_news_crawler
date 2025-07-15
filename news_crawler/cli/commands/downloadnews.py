import multiprocessing.synchronize
from .common import CommonArgs, GeneralOptions, CommonCmd
from .multiprocess import NewsWorker, launchMP_Workers
from typing import Dict, List
from datetime import datetime
import multiprocessing
import logging
from news_crawler.core.downloader import DownloadNewsJob, GeneralDownloader
from news_crawler.common.dates import get_range

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
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper()
        LOG.info(f"Query to Mongo: {basic_filter}") 
        nps = repos.newspaper.find_by(basic_filter)
        nps = list(nps)
        LOG.info(f"Found {len(nps)} newspapers to download")
        # Implement the logic to download news based on the provided arguments

        start,end = get_range(self.args.year, self.args.month, self.args.day)
        LOG.info(f"Downloading news from {start} to {end}")
        tasks = []
        manager = multiprocessing.Manager()
        lock = manager.Lock()

        for np in nps:
            filter= self.buildFilterArticles(np_short_name=np.short_name)
            filter["date"] = {"$gte": start, "$lt": end}
            articles = repos.articles.find_by(filter)
            articles = [article for article in articles if article.article_data is None]
            
            articles = articles[:min(5,len(articles))]  # Limit to 5 articles for each newspaper
            
            LOG.info(f"Found {len(articles)} articles to download of {np.name}")
            if len(articles) != 0:
                job = DownloadNewsJob(np,articles, lock, manager)
                tasks.append(job)
        
        workers = []

        for i in range(min(self.args.workers,len(tasks))):
            worker = DownloadWorker(f"DownloadWorker-{i}", tasks)
            workers.append(worker)

        launchMP_Workers(workers)

        pass