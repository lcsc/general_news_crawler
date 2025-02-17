import multiprocessing as mp
import logging
from .common import GeneralOptions, CommonArgs
from ...common.logtools import updateLogger
from ...common.consts import ccaa
from typing import List

LOG=logging.getLogger(__name__)

from datetime import datetime

def run_ca(target,ca,obj:GeneralOptions,args:CommonArgs):
    updateLogger()
    start =datetime.now()
    LOG.info(f"Start Procces for ca {ca}")
    obj.ccaa=ca
    target(obj,args)
    LOG.info(f"END Procces for ca {ca} in {datetime.now() -start}")

    

def launchMP_CA(target, obj: GeneralOptions, args: CommonArgs):
    updateLogger()
    workers = {}
    LOG.debug (obj)
    for ca in ccaa:
        p = mp.Process(target=run_ca, args=(target,ca,obj, args,), name=ca)
        workers[ca] = p
        p.start()

    for ca in ccaa:
        workers[ca].join()

class NewsWorker():
    def __init__(self,name:str):
        self.name=name
    
    def getTarget(self):
        pass
    def getArgs(self):
        pass

def run_worker(wd:NewsWorker):
    updateLogger()
    start =datetime.now()
    LOG.info(f"Start Procces for worker {wd.name}")
    target=wd.getTarget()
    target(wd.getArgs())
    LOG.info(f"END Procces for ca {wd.name} in {datetime.now() -start}")

def launchMP_Workers(workersData:List[NewsWorker]):
    updateLogger()
    workers = {}
    for wd in workersData:
        p = mp.Process(target=run_worker, args=(wd,), name=wd.name)
        workers[wd.name] = p
        p.start()

    for wd in workersData:
        workers[wd.name].join()

