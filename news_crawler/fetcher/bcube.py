from ..model.newspaper import NewsPaper
from .extractor import NewsPaperExtractor
from typing import List
from ..common.tools import print_exception
from ..model.repos import CrawlerRepos
from ..model.bcube import BcubePiMd

class BCubeExtractor(NewsPaperExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        self._engine = "bCube"

    def get_categories(self,np:NewsPaper)->BcubePiMd:
        return None

    # TODO List of Articles
    def extract_one_category(self,np,cat)->List[str]:
        return None
    
    # TODO List of Articles
    def extract_one(self,np:NewsPaper)-> List[str]:
        print(f"\nextracting {np.short_name}")
        categories = self.get_categories(np)
        # Si no hay categorias, no es de este extractor
        if categories is None:
            return None

        self._np_repos.bCubePiMd.save(categories)
        
        print(f"  found {len(categories.found_cats)} categories: {categories.found_cats}")
        for cat in categories.found_cats:
            try:
                self.extract_one_category(np,cat)  
            except Exception as e:
                print_exception(e)
        
        return None # None means this newspaper is not from this extractor


