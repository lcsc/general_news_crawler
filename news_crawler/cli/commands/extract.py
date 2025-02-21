from .common import CommonArgs,CommonCmd,GeneralOptions
from ...core.fetcher import NewsPaperExtractor
import logging

from ...bcube.fetcher import BCubePrensaIbericaExtractor
from ...wordpress.fetcher import WordPressInfoExtractor

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
        args:ExtractArgs=self.args
        
        if args.sub_engine is None or args.sub_engine == "PrensaIberica":
            extractor:NewsPaperExtractor = BCubePrensaIbericaExtractor(repos)
            candidates = extractor.get_candidates(try_no_engine=args._tryUnknown,filter=basic_filter)
            candidates = list(candidates)
            LOG.info(f"Found {len(candidates)} NewsPapers")

            extractor.extract_many(candidates)
        if args.sub_engine is None or args.sub_engine == "wp-json":
            extractor:NewsPaperExtractor = WordPressInfoExtractor(repos)
            candidates = extractor.get_candidates(try_no_engine=args._tryUnknown,filter=basic_filter)
            candidates = list(candidates)
            LOG.info(f"Found {len(candidates)} NewsPapers")
            extractor.extract_many(candidates)
        pass