from pymongo import database
from .newspaper import NewsPaperRepository
from .bcube import BcubePiMDRepository, PrensaIbericaStatRepository

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
            self.bCubePiMd = None
            self.piStats= None
        # else:
        #     print("Skiping init")
    
    def connect(self,db:database=None):
        print ("Connecting to DataBase")
        self.newspaper = NewsPaperRepository(database=db)
        self.bCubePiMd = BcubePiMDRepository(database=db)
        self.piStats= PrensaIbericaStatRepository(database=db)

        return self
