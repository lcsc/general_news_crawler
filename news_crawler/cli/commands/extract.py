from .common import CommonArgs,CommonCmd,GeneralOptions
from ...core.fetcher import NewsPaperExtractor
import logging

from ...bcube.fetcher import BCubePrensaIbericaExtractor

LOG = logging.getLogger(__name__)

class ExtractArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,tryUnknown:bool):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self._tryUnknown=tryUnknown

    
class ExtractCmd(CommonCmd):
    
    def __init__(self, general:GeneralOptions,args:ExtractArgs ):
        super().__init__(general=general,args=args)

    def extract(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper();
        LOG.info(f"Query to Mongo: {basic_filter}") 
        candidates = repos.newspaper.find_by(basic_filter)
        candidates = list(candidates)
        LOG.info(f"Found {len(candidates)} NewsPapers")
        
        extractor:NewsPaperExtractor = BCubePrensaIbericaExtractor(repos)

        extractor.extract_many(candidates)
        
        pass