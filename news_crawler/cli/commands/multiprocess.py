import multiprocessing as mp
import logging
from .common import GeneralOptions, CommonArgs
from ...common.loggin import updateLogger
from ...common.consts import ccaa
LOG=logging.getLogger(__name__)


def run_ca(target,ca,obj:GeneralOptions,args:CommonArgs):
    updateLogger()
    obj.ccaa=ca
    target(obj,args)

    

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

