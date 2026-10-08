from .common import CommonArgs,CommonCmd,GeneralOptions
from ...core.fetcher import NewsPaperExtractor
import logging

from ...bcube.fetcher import BCubePrensaIbericaExtractor
from ...wordpress.fetcher import WordPressInfoExtractor
from ...vocento.fetcher import VocentoInfoExtractor

from ...common.consts import ENGINE_ID_bCube,ENGINE_ID_WordPress,ENGINE_ID_Vocento
from ...common.consts import SUBENGINE_ID_bc_PrensaIberica,SUBENGINE_ID_wp_json,SUBENGINE_ID_vc_v22

from typing import List

LOG = logging.getLogger(__name__)

class ExtractArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,tryUnknown:bool,force:bool):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self._tryUnknown=tryUnknown
        self._force=force

    
class ExtractCmd(CommonCmd):
    
    def __init__(self, general:GeneralOptions,args:ExtractArgs ):
        super().__init__(general=general,args=args)

    def extract(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper();
        LOG.info(f"Query to Mongo: {basic_filter}") 
        args:ExtractArgs=self.args
        
        extractors:List[NewsPaperExtractor] = []
        if args.engine is None or args.engine == ENGINE_ID_bCube:
            if args.sub_engine is None or args.sub_engine == SUBENGINE_ID_bc_PrensaIberica:
                extractors.append(BCubePrensaIbericaExtractor(repos))
        if args.engine is None or args.engine == ENGINE_ID_WordPress:
            if args.sub_engine is None or args.sub_engine == SUBENGINE_ID_wp_json:
                extractors.append(WordPressInfoExtractor(repos))
        if args.engine is None or args.engine == ENGINE_ID_Vocento:
            if args.sub_engine is None or args.sub_engine == SUBENGINE_ID_vc_v22:
                extractors.append(VocentoInfoExtractor(repos))

            
        for extractor in extractors:
            candidates = extractor.get_candidates(try_no_engine=args._tryUnknown,filter=basic_filter)
            candidates = list(candidates)
            LOG.info(f"Found {len(candidates)} NewsPapers for extractor {extractor.__class__.__name__}")
            extractor.extract_many(candidates, force= args._force)

        