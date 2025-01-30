from ..model.newspaper import NewsPaperRepository,NewsPaper
from typing import List
from ..common.tools import print_exception

class NewsPaperExtractor():

    def __init__(self,np_repo:NewsPaperRepository):
        self._np_repo = np_repo
        self._engine = None
        self._subengine = None
    
    def get_no_engine(self):
        return self._np_repo.find_by({"engine":None,"real_url":{"$ne":None}})
    
    def get_engine_no_subengine(self):
        return self._np_repo.find_by({"engine.engine":self._engine,"engine.subengine":None})
    
    def get_engine_subengine(self):
        return self._np_repo.find_by({"engine.engine":self._engine,"engine.subengine":self._subengine})

    def get_candidates(self)->List[NewsPaper]:
        ret = []
        ret.extend(self.get_no_engine())
        if self._engine is not None:
            ret.extend(self.get_engine_no_subengine())
            if self._subengine is not None:
                ret.extend(self.get_engine_subengine())
        return ret


    # TODO List of Articles
    def extract_one(self,np:NewsPaper)-> List[str]:
        # should be implemented by the subclasses
        return None

    def should_be_extracted(self,np:NewsPaper)->bool:

        return True

    def extract_all(self):
        cand= self.get_candidates()
        for np in cand:
            if self.should_be_extracted(np):
                try:
                    articles = self.extract_one(np)
                    if articles is not None:
                        self._np_repo.save(np)
                except Exception as e:
                    print_exception(e)
