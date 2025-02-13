import click

from .commands.common import GeneralOptions, CommonArgs
from .commands.backfill import BackFillArgs, BackFillCmd
from ..common.consts import engines
from ..common.consts import sub_engines
from .commands.multiprocess import launchMP_CA
from datetime import datetime

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


def run_backfillnews(obj:GeneralOptions,args:CommonArgs):
    filler= BackFillCmd(general=obj,args=args)
    filler.backFillNews()


@main.command()
@click.option('-e',"engine", type=click.Choice(engines, case_sensitive=False), default=None)
@click.option('-se',"sub_engine",type=click.Choice(sub_engines, case_sensitive=False), default=None)
@click.argument('year',type=int)
@click.argument('month',type=int,required=False)
@click.argument('day',type=int, required=False)
@click.pass_obj
def backfillnews(obj:GeneralOptions,engine:str,sub_engine:str,year:int,month:int,day:int):
    start = datetime.now()

    print("BackFilling")
    args = BackFillArgs(engine=engine,sub_engine=sub_engine,
        year=year,month=month,day=day)

    if obj.ccaa is None:
        launchMP_CA(run_backfillnews,obj,args)
    else:
        run_backfillnews(obj,args)

    print(f"Duration: {datetime.now()-start}")

