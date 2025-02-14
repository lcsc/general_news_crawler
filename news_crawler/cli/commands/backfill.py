from .common import CommonArgs, GeneralOptions, CommonCmd
import logging
from time import sleep
from ...core.backfiller.backfiller import BackFiller,BackFillerManager
from ...backfiller.wordpress import WpBackFiller

from typing import List,Dict
LOG:logging.Logger=logging.getLogger(__name__)


class BackFillArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,year:int,month:int,day:int):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self.year=year
        self.month=month
        self.day=day
        self._bfillers:Dict[str,BackFiller]

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

        arg:BackFillArgs=self.args

        mgr = BackFillerManager(repos)
        mgr.addBackFiller(WpBackFiller(repos))
        mgr.backfillManyNews(candidates,arg.year,arg.month,arg.day)
            
            

        pass
                        