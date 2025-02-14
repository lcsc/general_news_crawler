from pymongo import database
from .newspaper import NewsPaperRepository,NewsArticleRepository
from ...bcube.model.prensaiberica import BcubePiMDRepository, PrensaIbericaStatRepository
from ...bcube.model.bcube import BcubeCategoryRepository

import logging
LOG = logging.getLogger(__name__)

class CrawlerRepos:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(CrawlerRepos, cls).__new__(cls)
        # else:
        #     print ("Reusing Singleton")
        return cls._instance
    
    def __init__(self):
        # print("Running  init")
        if not hasattr(self, "newspaper"):
            self.newspaper = None
            self.articles= None

            self.bCubeCategories = None
            self.bCubePiMd = None
            self.piStats= None
            
        # else:
        #     print("Skiping init")
    
    def connect(self,db:database=None):
        LOG.info ("Connecting to DataBase")
        self.newspaper = NewsPaperRepository(database=db)
        self.articles= NewsArticleRepository(database=db)

        self.bCubeCategories=BcubeCategoryRepository(database=db)
        self.bCubePiMd = BcubePiMDRepository(database=db)
        self.piStats= PrensaIbericaStatRepository(database=db)

        return self
