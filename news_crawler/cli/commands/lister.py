from .common import CommonArgs,CommonCmd,GeneralOptions
from ...core.newspapers import PRENSA_DIGITAL_ID, PRENSA_ESCRITA_ID, PrensaDigitalLister, PrensaEscritaLister

import logging

LOG = logging.getLogger(__name__)

class ListerArgs(CommonArgs):
    def __init__(self, lister:str=None):
        super().__init__(engine=None,sub_engine=None)
        self._lister=lister

    
class ListerCmd(CommonCmd):
    
    def __init__(self, general:GeneralOptions,args:ListerArgs ):
        super().__init__(general=general,args=args)

    def list(self):
        global PRENSA_DIGITAL_ID
        global PRENSA_ESCRITA_ID

        repos = self.connectMongo()
        listers = []
        args:ListerArgs = self.args
        LOG.info(f"Buscando Periodicos de: {args._lister}")
        if args._lister == PRENSA_DIGITAL_ID:
            listers=[PrensaDigitalLister(repos.newspaper)]
        elif args._lister == PRENSA_ESCRITA_ID: 
            listers=[PrensaEscritaLister(repos.newspaper)]
        elif args._lister == None: 
            listers=[PrensaDigitalLister(repos.newspaper),PrensaEscritaLister(repos.newspaper)]
        
        for l in listers:
            res =l.get_newspapers(self.general.ccaa,self.general.provincia)
            LOG.info(f"found {len(res)} ")
            l.store_newspapers(res)
    
            
            
