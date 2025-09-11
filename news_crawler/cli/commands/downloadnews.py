import multiprocessing.synchronize

from news_crawler.core.model.newspaper import NewsArticle
from .common import CommonArgs, GeneralOptions, CommonCmd
from .multiprocess import NewsWorker, launchMP_Workers
from typing import Dict, List
from datetime import datetime
import multiprocessing
import logging
from news_crawler.core.downloader import DownloadNewsJob, GeneralDownloader
from news_crawler.common.dates import get_range
from news_crawler.common.consts import DownloadStatus_NOT_FOUND

LOG:logging.Logger=logging.getLogger(__name__)

class DownloadNewsArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,year:int,month:int,day:int, workers:int,delay:float):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self.year=year
        self.month=month
        self.day=day
        self.workers=workers
        self.delay=delay
        #self._bfillers:Dict[str,BackFiller]




def doDownloadNewsMp(data):
    general:GeneralOptions = None
    download_args:DownloadNewsArgs = None
    name, tasks, general, download_args = data
    cmd = CommonCmd(general,None)
    repos = cmd.connectMongo()
    downloader=GeneralDownloader(name, tasks,repos,
                                 min_np_Delay_s=download_args.delay,
                                 #report_interval_m=1
                                 )
    downloader.donwload()



class  DownloadWorker(NewsWorker):
    def __init__(self, name:str, args:List, general:GeneralOptions, download_args:DownloadNewsArgs):
        super().__init__(name)
        self.args = args
        self.general = general
        self.download_args = download_args

    def getTarget(self):
        return doDownloadNewsMp

    def getArgs(self):
        return (self.name,self.args,self.general,self.download_args)



class DownloadNewsCmd(CommonCmd):
    def __init__(self, general:GeneralOptions, args:DownloadNewsArgs):
        super().__init__(general, args)
        self.args = args
    def _isArticleDownloable(self,article:NewsArticle) -> bool:
        # Check if the article is downloadable
        # it is downloable if it has no data but its status is not "downloaded"
        # so we invert the logic, if we have data, don't download,
        # No data but status is "not found" (404) means we can't download
        # other cases means we can download

        # in future versions we can add a parametter to retry 404

        if article.article_data is not None: return False
        if article.download_status and article.download_status == DownloadStatus_NOT_FOUND: return False

        return True

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
            if np.n_articulos is None or np.n_articulos < 1:
                LOG.warning(f"Newspaper {np.name} has no articles to download, skipping")
                continue
            filter= self.buildFilterArticles(np_short_name=np.short_name)
            filter["date"] = {"$gte": start, "$lt": end}
            articles = repos.articles.find_by(filter)
            articles = [article for article in articles if self._isArticleDownloable(article)]
            
            # articles = articles[:min(2,len(articles))]  # Limit to 5 articles for each newspaper
            # articles = [article for article in articles if article.article_url.endswith(".pdf")]
            
            LOG.info(f"Found {len(articles)} articles to download of {np.name}")
            if len(articles) != 0:
                job = DownloadNewsJob(np,articles, lock, manager)
                tasks.append(job)
        
        workers = []

        for i in range(min(self.args.workers,len(tasks))):
            worker = DownloadWorker(f"DownloadWorker-{i}", tasks,self.general, self.args)
            workers.append(worker)

        launchMP_Workers(workers)

        pass