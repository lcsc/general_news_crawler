from .common import CommonArgs, GeneralOptions, CommonCmd
import logging
from time import sleep
from ...core.detector.detector import NewsPaperDetector

from typing import List,Dict
LOG:logging.Logger=logging.getLogger(__name__)

class DetectArgs(CommonArgs):
    def __init__(self, detector:str=None):
        super().__init__(engine=None,sub_engine=None)
        self._detector=detector

        

class DetectCmd(CommonCmd):
    def __init__(self, general:GeneralOptions,args:DetectArgs ):
        super().__init__(general=general,args=args)

    def detect(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper();
        LOG.info(f"Query to Mongo: {basic_filter}") 
        candidates = repos.newspaper.find_by(basic_filter)
        candidates = list(candidates)
        LOG.info(f"Found {len(candidates)} NewsPapers")
        detector =  NewsPaperDetector(repo=repos.newspaper)
        detector.detect_many(candidates)