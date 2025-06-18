from .common import CommonArgs, GeneralOptions, CommonCmd
import logging

LOG:logging.Logger=logging.getLogger(__name__)

class DownloadNewsArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,year:int,month:int,day:int, workers:int):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self.year=year
        self.month=month
        self.day=day
        self.workers=workers
        #self._bfillers:Dict[str,BackFiller]

class DownloadNewsCmd(CommonCmd):
    def __init__(self, general:GeneralOptions, args:DownloadNewsArgs):
        super().__init__(general, args)
        self.args = args

    def downloadNews(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterArticles()
        LOG.info(f"Query to Mongo: {basic_filter}") 
        articles = repos.articles.find_by(basic_filter)
        articles = [article for article in articles if article.article_data is None]
        LOG.info(f"Found {len(articles)} articles to download")
        # Implement the logic to download news based on the provided arguments
        pass