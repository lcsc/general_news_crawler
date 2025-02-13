from ...common.tools import connect_mongo
from ...model.repos import CrawlerRepos

from pymongo import MongoClient, database


class GeneralOptions():
    def __init__(self,
                 ccaa: str,
                 provincia: str,
                 short_name: str,
                 mongo_url: str,
                 mongo_user: str,
                 mongo_passwd: str):
        self.ccaa: str = ccaa
        self.provincia: str = provincia
        self.short_name: str = short_name
        self.mongo_url: str = mongo_url
        self.mongo_user: str = mongo_user
        self.mongo_passwd: str = mongo_passwd


class CommonArgs():
    def __init__(self, engine: str, sub_engine: str):
        self.engine: str = engine
        self.sub_engine: str = sub_engine


class CommonCmd():
    def __init__(self, general: GeneralOptions, args: CommonArgs):
        self.general = general
        self.args = args
        self.mongoClient: MongoClient = None
        self.dataBase: database = None
        self.repos: CrawlerRepos = None

    def connectMongo(self) -> CrawlerRepos:
        if self.mongoClient is None:
            self.mongoClient = connect_mongo(mongo_url=self.general.mongo_url,
                                             username=self.general.mongo_user,
                                             password=self.general.mongo_passwd)
        if self.dataBase is None:
            self.dataBase = self.mongoClient["general_news"]
        if self.repos is None:
            self.repos = CrawlerRepos().connect(self.dataBase)
        return self.repos

    def buildFilterNewsPaper(self)->dict:
        ret = {}
        if self.general.ccaa is not None:
            ret.update({"ccaa":self.general.ccaa})
        if self.general.provincia is not None:
            ret.update({"provincia":self.general.provincia})
        if self.general.short_name is not None:
            ret.update({"short_name":self.general.short_name})
        if self.args is not None:
            if self.args.engine is not None:
                ret.update({"engine.engine":self.args.engine})
            if self.args.sub_engine is not None:
                ret.update({"engine.sub_engine":self.args.sub_engine})

        return ret
