import click

from .commands import GeneralOptions, CommonArgs
from .commands import BackFillArgs, BackFillCmd
from .commands import DetectArgs,DetectCmd
from ..common.consts import engines
from ..common.consts import sub_engines
from .commands import launchMP_CA

from .commands import ListerArgs,ListerCmd
from .commands import ExtractArgs, ExtractCmd
from .commands import UploaderCmd
from .commands import DownloadNewsArgs, DownloadNewsCmd
from .commands import FixArticlesProvs
from .commands import ClassifyHeadLines

from ..core.newspapers import Listers

from datetime import datetime

import logging
LOG = logging.getLogger(__name__)

@click.group()
@click.option('-c','--ccaa', 'ccaa', envvar='REPO_HOME', default=None)
@click.option('-p','--provincia', 'provincia', envvar='REPO_HOME', default=None)
@click.option('-s','--short_name', 'short_name', envvar='REPO_HOME', default=None)
@click.option('--mongo_url', 'mongo_url', envvar='MONGODB_URL', default='mongodb://root:example@mongodb:27017/')
@click.option('--mongo_user', 'mongo_user', envvar='MONGODB_USERNAME', default='root')
@click.option('--mongo_passwd', 'mongo_passwd', envvar='MONGODB_PASSWORD', default='example')
@click.pass_context
def main(ctx, ccaa:str,
        provincia:str,
        short_name:str,
        mongo_url:str,
        mongo_user:str,
        mongo_passwd:str):
    ctx.obj = GeneralOptions(ccaa,
        provincia,
        short_name,
        mongo_url,
        mongo_user,
        mongo_passwd)
    pass

@main.command()
@click.argument("lister",type=click.Choice(Listers, case_sensitive=False), default=None, required=False)
@click.pass_obj
def list(obj:GeneralOptions,lister:str):
    arg = ListerArgs(lister)
    cmd = ListerCmd(obj,arg)
    cmd.list()
    pass


def do_detect(obj:GeneralOptions,args:DetectArgs):
    detector= DetectCmd(general=obj,args=args)
    detector.detect()

@main.command()
@click.pass_obj
def detect(obj:GeneralOptions):
    start = datetime.now()

    LOG.info("Detecting")
    args = DetectArgs()

    if obj.ccaa is None:
        launchMP_CA(do_detect,obj,args)
    else:
        do_detect(obj,args)

    LOG.info(f"Total Duration: {datetime.now()-start}")


def do_extract(obj:GeneralOptions, args:ExtractArgs):
    extractor =ExtractCmd(obj,args)
    extractor.extract()

@main.command()
@click.option('-e',"engine", type=click.Choice(engines, case_sensitive=False), default=None)
@click.option('-se',"sub_engine",type=click.Choice(sub_engines, case_sensitive=False), default=None)
@click.option('-t/-nt','--try/--no-try',"tryUnknown", default=True)
@click.option('-f/-nf','--force/--no-force',"force", default=False)
@click.pass_obj
def extract(obj:GeneralOptions,engine:str,sub_engine:str,tryUnknown:bool,force:bool):
    start = datetime.now()

    LOG.info("Extracting dates")
    args = ExtractArgs(engine=engine,sub_engine=sub_engine,
        tryUnknown=tryUnknown, force=force)
    if obj.ccaa is None:
        launchMP_CA(do_extract,obj,args)
        #do_extract(obj,args)
    else:
        do_extract(obj,args)

    LOG.info(f"Total Duration: {datetime.now()-start}")
    

    pass


def run_backfillnews_day(obj:GeneralOptions,args:CommonArgs):
    filler= BackFillCmd(general=obj,args=args)
    filler.backFillNews_day()


@main.command()
@click.option('-e',"engine", type=click.Choice(engines, case_sensitive=False), default=None)
@click.option('-se',"sub_engine",type=click.Choice(sub_engines, case_sensitive=False), default=None)
@click.option('-w',"workers",type=int,default=10)
@click.argument('year',type=int)
@click.argument('month',type=int,required=False)
@click.argument('day',type=int, required=False)
@click.pass_obj
def backfillnews(obj:GeneralOptions,engine:str,sub_engine:str,workers:int,year:int,month:int,day:int):
    start = datetime.now()

    LOG.info("BackFilling")
    args = BackFillArgs(engine=engine,sub_engine=sub_engine,
        year=year,month=month,day=day,workers=workers)

    if  obj.ccaa is not None and obj.short_name is not None:
         # nos piden un Periodico concreto
        if month is not None:
            # Si solo se genera un Job (y ya lo sabemos)
            run_backfillnews_day(obj,args)
            LOG.info(f"Total Duration: {datetime.now()-start}")
            return
    
    filler= BackFillCmd(general=obj,args=args)
    filler.backFillNews()
    LOG.info(f"Total Duration: {datetime.now()-start}")


def do_Upload(obj:GeneralOptions,args:CommonArgs):
    cmd = UploaderCmd(obj)
    cmd.upload()


# @main.command()
# @click.pass_obj
# def save_dir(obj:GeneralOptions):
#     start = datetime.now()

#     LOG.info("Uploading")
#     args = DetectArgs()

#     if obj.ccaa is None:
#         launchMP_CA(do_Upload,obj,args)
#     else:
#         do_Upload(obj,args)

#     LOG.info(f"Total Duration: {datetime.now()-start}")

def run_downloadnews_day(obj:GeneralOptions,args:CommonArgs):
    filler= DownloadNewsCmd(general=obj,args=args)
    filler.downloadNews()


@main.command()
@click.option('-e',"engine", type=click.Choice(engines, case_sensitive=False), default=None)
@click.option('-se',"sub_engine",type=click.Choice(sub_engines, case_sensitive=False), default=None)
@click.option('-w',"workers",type=int,default=10)
@click.option('-d',"delay",type=float,default=13.0)
@click.argument('year',type=int)
@click.argument('month',type=int,required=False)
@click.argument('day',type=int, required=False)
@click.pass_obj
def downloadnews(obj:GeneralOptions,engine:str,sub_engine:str,delay:float,workers:int,year:int,month:int,day:int):
    start = datetime.now()

    LOG.info("Downloading news")
    args = DownloadNewsArgs(engine=engine,sub_engine=sub_engine,
        year=year,month=month,day=day,workers=workers, delay=delay)

    if  obj.ccaa is not None and obj.short_name is not None:
         # nos piden un Periodico concreto
        if month is not None:
            # Si solo se genera un Job (y ya lo sabemos)
            run_downloadnews_day(obj,args)
            LOG.info(f"Total Duration: {datetime.now()-start}")
            return
    
    filler= DownloadNewsCmd(general=obj,args=args)
    filler.downloadNews()
    LOG.info(f"Total Duration: {datetime.now()-start}")

# Arreglar provincias de los articulos de los periodicos
def do_fix_articles_provs(obj:GeneralOptions,args:CommonArgs):
    cmd = FixArticlesProvs(obj,args)
    cmd.fixArticlesProvs()

@main.command()
@click.pass_obj
def fixarticlesprov(obj:GeneralOptions):
    start = datetime.now()

    args = DetectArgs()

    if obj.ccaa is None:
        launchMP_CA(do_fix_articles_provs,obj,args)
    else:
        do_fix_articles_provs(obj,args)

    LOG.info(f"Total Duration: {datetime.now()-start}")

# Clasificar headlines de sequeas
def do_classify_headlines(obj:GeneralOptions,args:CommonArgs):
    cmd = ClassifyHeadLines(obj,args)
    cmd.classifyHeadLines()

@main.command()
@click.pass_obj
def classifyHeadLines(obj:GeneralOptions):
    start = datetime.now()

    args = DetectArgs()

    if obj.ccaa is None:
        launchMP_CA(do_classify_headlines,obj,args)
    else:
        do_classify_headlines(obj,args)

    LOG.info(f"Total Duration: {datetime.now()-start}")