from ..model.newspaper import NewsPaper
from typing import List
from ..common.tools import print_exception
from ..model.repos import CrawlerRepos

class NewsPaperExtractor():

    def __init__(self,np_repos:CrawlerRepos):
        self._np_repos = np_repos
        self._engine = None
        self._subengine = None
    
    def get_no_engine(self):
        return self._np_repos.newspaper.find_by({"engine":None,"real_url":{"$ne":None}})
    
    def get_engine_no_subengine(self):
        return self._np_repos.newspaper.find_by({"engine.engine":self._engine,"engine.subengine":None})
    
    def get_engine_subengine(self):
        if self._subengine is None:
            return []
        return self._np_repos.newspaper.find_by({"engine.engine":self._engine,"engine.subengine":self._subengine})

    def get_candidates(self)->List[NewsPaper]:
        '''

        '''
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
        # has to extract n_articles,
        # First declared news
        # First Month with 20+ articles
        return None

    def should_be_extracted(self,np:NewsPaper)->bool:
        # TODO Implement a basic filter
        return True
    
    def _process_one(self, np:NewsPaper):
        articles = self.extract_one(np)
        if articles is not None:
            self._np_repo.save(np)


    def extract_all(self):
        cand= self.get_candidates()
        for np in cand:
            if self.should_be_extracted(np):
                try:
                    self._process_one(np)
                except Exception as e:
                    print_exception(e)
