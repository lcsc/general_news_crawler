import click

from .commands import GeneralOptions, CommonArgs
from .commands import BackFillArgs, BackFillCmd
from .commands import DetectArgs,DetectCmd
from ..common.consts import engines
from ..common.consts import sub_engines
from .commands import launchMP_CA
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
