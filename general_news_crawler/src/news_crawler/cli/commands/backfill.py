from .common import CommonArgs, GeneralOptions, CommonCmd
import logging
from time import sleep
from ...core.backfiller.backfiller import BackFiller,BackFillerManager
from ...wordpress.backfiller.wordpress import WpBackFiller
from ...bcube.backfiller.prensaiberica import BcubePiBackFiller
from ...vocento.backfiller.vocento import VocentoBackFiller
from ...core.model.newspaper import NewsPaper
from ...common.consts import BfStatus_OK

from .multiprocess import NewsWorker, launchMP_Workers

from typing import List,Dict
LOG:logging.Logger=logging.getLogger(__name__)


class BackFillArgs(CommonArgs):
    def __init__(self, engine:str,sub_engine:str,year:int,month:int,day:int, workers:int):
        super().__init__(engine=engine,sub_engine=sub_engine)
        self.year=year
        self.month=month
        self.day=day
        self.workers=workers
        self._bfillers:Dict[str,BackFiller]

class BackFillJob():
    def __init__(self, general:GeneralOptions,np:NewsPaper,year:int,month:int,day:int=None):
        self.general = general
        self.np=np
        self.year=year
        self.month=month
        self.day=day
        pass

def getGroupedJobs(jobs:List[BackFillJob])->Dict[str,List[BackFillJob]]:
    ret:Dict[str,List[BackFillJob]] ={}
    for j in jobs:
        key:str=None
        if j.day is None:
            key = f"{j.year}-{j.month}"
        else:
            key= f"{j.year}-{j.month}-{j.day}"
        if key not in ret:
            ret[key]=[]
        ret[key].append(j)
    return ret

def getNewsPapers(jobs:List[BackFillJob])->List[NewsPaper]:
    ret=[]
    for j in jobs:
        ret.append(j.np)
    return ret

def doBackFillMp(jobs:List[BackFillJob]):
    if len(jobs) == 0: return
    cmd = CommonCmd(jobs[0].general,None)
    repos = cmd.connectMongo()
    mgr = BackFillerManager(repos)
    mgr.addBackFiller(WpBackFiller(repos))
    mgr.addBackFiller(BcubePiBackFiller(repos))
    mgr.addBackFiller(VocentoBackFiller(repos))
    
    grouped = getGroupedJobs(jobs)
    LOG.debug(f"Grouped Jobs {len(grouped)}")
    for key in grouped:
        month_jobs = grouped[key]
        base = month_jobs[0]
        nps = getNewsPapers(month_jobs)
        mgr.backfillManyNews(nps,base.year,base.month,base.day)


class BackFillWorker(NewsWorker):
    def __init__(self,name:str):
        super().__init__(name)
        self.jobs:List[BackFillJob]=[]
        self.nJobs=0
        
    def addJobs(self,jobs:List[BackFillJob]):
        self.jobs.extend(jobs)
        self.nJobs += len(jobs)
    def getArgs(self):
        return self.jobs
    def getTarget(self):
        return doBackFillMp

class BackFillCmd(CommonCmd):
    def __init__(self, general:GeneralOptions,args:BackFillArgs ):
        super().__init__(general=general,args=args)

    def backFillNews_day(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper();
        LOG.info(f"Query to Mongo: {basic_filter}") 
        candidates = repos.newspaper.find_by(basic_filter)
        candidates = list(candidates)
        LOG.info(f"Found {len(candidates)} NewsPapers")

        arg:BackFillArgs=self.args

        mgr = BackFillerManager(repos)
        mgr.addBackFiller(WpBackFiller(repos))
        mgr.addBackFiller(BcubePiBackFiller(repos))
        mgr.addBackFiller(VocentoBackFiller(repos))
        mgr.backfillManyNews(candidates,arg.year,arg.month,arg.day)
        pass

    def expandJob(self,np:NewsPaper,year:int, month:int)->BackFillJob:
        ret = BackFillJob(general=self.general,np=np,year=year,month=month,day=None)
        
        year = str(year)
        month= str(month)
        
        # No BackFill
        if np.backfill is None: return ret
        # No year or is null
        if year not in np.backfill: return ret
        if np.backfill[year] is None: return ret
        # No Month or ir null
        if month not in np.backfill[year]: return ret
        if np.backfill[year][month] is None: return ret
        # Hay descarga pero no es OK
        if np.backfill[year][month].status == BfStatus_OK:
            return None
        else:
            return ret

        return None

    def expandJobs(self,np:NewsPaper,year:int, month:int, day:int=None)->List[BackFillJob]:
        if day is not None:
            return [BackFillJob(general=self.general,np=np,year=year,month=month,day=day)]
        ret = []
        months:List[int]=None

        if month is not None:
            months=[month]
        else:
            months=range(12,0,-1)

        for m in months:
            job = self.expandJob(np,year,m)
            if job is not None:
                ret.append(job)
        return ret

    def find_less_loaded_worker(self,workers:List[BackFillWorker])->BackFillWorker:
        ret = workers[0]
        for w in workers:
            if ret.nJobs > w.nJobs: ret = w
        return ret

    def splitJobs(self,jobs:List[Dict])->List[BackFillWorker]:
        ret:List[BackFillWorker] = []
        args:BackFillArgs=self.args
        for n in range (args.workers):
            ret.append(BackFillWorker(f"BackFill-{n}"))

        for job in jobs:
            w=self.find_less_loaded_worker(ret)
            w.addJobs(job["jobs"])
        
        return ret 


    def backFillNews(self):
        repos = self.connectMongo()
        basic_filter= self.buildFilterNewsPaper();
        LOG.info(f"Query to Mongo: {basic_filter}") 
        candidates = repos.newspaper.find_by(basic_filter)
        candidates = list(candidates)
        LOG.info(f"Found {len(candidates)} NewsPapers")
        arg:BackFillArgs=self.args
        jobs = []
        for np in candidates:
            np_jobs = self.expandJobs(np,arg.year,arg.month,arg.day)

            if len(np_jobs)>0:
                jobs.append({"np":np,"jobs":np_jobs,"nJobs":len(np_jobs)})
        
        workers = self.splitJobs(jobs)
        for w in workers: LOG.debug(f"{w.name} -> {w.nJobs}")
        
        launchMP_Workers(workers)

        pass

