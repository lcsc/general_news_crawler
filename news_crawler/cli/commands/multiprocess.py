import multiprocessing as mp
import logging
from .common import GeneralOptions, CommonArgs
from ...common.logtools import updateLogger
from ...common.consts import ccaa
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

