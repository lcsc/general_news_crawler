from .common import CommonArgs, GeneralOptions, CommonCmd
import logging
from time import sleep

LOG:logging.Logger=logging.getLogger(__name__)


class BackFillArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,year:int,month:int,day:int):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self.year=year
        self.month=month
        self.day=day

class BackFillCmd(CommonCmd):
    def __init__(self, general:GeneralOptions,args:BackFillArgs ):
        super().__init__(general=general,args=args)

    def backFillNews(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper();
        LOG.info(f"Query to Mongo: {basic_filter}") 

        candidates = repos.newspaper.find_by(basic_filter)
        candidates = list(candidates)
        LOG.info(f"Found {len(candidates)} NewsPapers")

        for np in candidates:
             LOG.info(np.short_name)

        pass
                        