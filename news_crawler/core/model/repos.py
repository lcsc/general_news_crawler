from pymongo import database
from pymongo.synchronous.collection import Collection
from .newspaper import NewsPaperRepository,NewsArticleRepository
from ...bcube.model.prensaiberica import BcubePiMDRepository, PrensaIbericaStatRepository
from ...bcube.model.bcube import BcubeCategoryRepository
from .files import FileDb,FilesRepository
import logging
LOG = logging.getLogger(__name__)

from datetime import datetime,timezone,timedelta

import tarfile
import os



class CrawlerRepos:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(CrawlerRepos, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "newspaper"):
            self.newspaper = None
            self.articles= None

            self.bCubeCategories = None
            self.bCubePiMd = None
            self.piStats= None
    
    def connect(self,db:database=None):
        LOG.info ("Connecting to DataBase")
        self.newspaper = NewsPaperRepository(database=db)
        self.articles= NewsArticleRepository(database=db)

        self.bCubeCategories=BcubeCategoryRepository(database=db)
        self.bCubePiMd = BcubePiMDRepository(database=db)
        self.piStats= PrensaIbericaStatRepository(database=db)
        self.db=db

        return self
    
    def save_file(self, path:str, contents:any, group:str, dateNewer:datetime):
        
        if isinstance(dateNewer,str):
            dateNewer=datetime.fromisoformat(dateNewer)
        if dateNewer.tzinfo is None:
            dateNewer=dateNewer.replace(tzinfo=timezone.utc)

        repo_name=path.split("/")
        repo_name=f"{repo_name[0]}_{repo_name[1]}"
        #LOG.debug(f"Using {repo_name}")
        files:Collection = self.db[repo_name]
        file = files.find_one({"path":path,"group":group})
        


        if file is None:
            file = {"path":path,"group":group,"format":"string","contents":contents,"modDate":dateNewer}
            files.insert_one(file)
            return
        
        if file["modDate"].tzinfo is None:
            file["modDate"]=file["modDate"].replace(tzinfo=timezone.utc)


        if dateNewer > file["modDate"] \
            and (dateNewer - file["modDate"] ) > timedelta(seconds=1):
            
            LOG.debug(f"Updating ... {path}")
      
            file["contents"]=contents
            file["modDate"]=dateNewer
            files.update_one(file)
        pass

    def save_file_tar(self, path:str, contents:any, group:str, dateNewer:datetime):
        

        dir = os.path.dirname(path)
        filename = os.path.basename(path)

        #LOG.debug(f"Saving {filename} of {dir}")
        
        tarname=f"{dir}/{group}.tar"
        if os.path.exists(tarname):
            with tarfile.open(tarname, "r") as tar:
                files = tar.getnames()
                if filename in files:
                    if isinstance(dateNewer,str):
                        dateNewer=datetime.fromisoformat(dateNewer)
                    if dateNewer.tzinfo is None:
                        dateNewer=dateNewer.replace(tzinfo=timezone.utc)
                    info = tar.getmember(filename)
                    mtime = datetime.fromtimestamp(info.mtime, tz=timezone.utc)
                    if dateNewer>mtime:
                        LOG.debug("needs update")
                    else:
                        #LOG.debug("Already on hd")
                        return

        
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        with open(path, 'w', newline='') as file:
                file.write(contents)

        tarname=f"{dir}/{group}.tar"
        with tarfile.open(tarname, "a") as tar:
            files = tar.getnames()
            #LOG.debug(files)
            tar.add(path,arcname=filename)
        
        
        os.unlink(path)

            
        
