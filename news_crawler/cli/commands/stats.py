
from news_crawler.cli.commands.common import CommonArgs, CommonCmd, GeneralOptions
from news_crawler.common.dates import get_range
from news_crawler.core.model.repos import CrawlerRepos
from news_crawler.common.consts import provincias
import csv

import logging
LOG = logging.getLogger(__name__)

def stats_provs(repos:CrawlerRepos, year:int):
    data = []
    start,end = get_range(year)
    for ccaa in provincias:
        for provincia in provincias[ccaa]:
            LOG.info(f"Processing {ccaa} - {provincia}")
            np_count = len( list( repos.newspaper.find_by( {"ccaa":ccaa,"provincia":provincia} ) ) )
            if np_count==0:
                provincia= None
                np_count = len( list( repos.newspaper.find_by( {"ccaa":ccaa,"provincia":provincia} ) ) )
            art_count = len( list( repos.articles.find_by( {"np_ccaa":ccaa,"np_provincia":provincia, "date":{"$gte": start, "$lt": end}} ) ) )
            
            data.append( {"ccaa":ccaa,"provincia":provincia,"newspaper_count":np_count,"article_count":art_count} )
    return data

def stats_ccaa(repos:CrawlerRepos, year:int):
    data = []
    start,end = get_range(year)
    for ccaa in provincias:
    
        LOG.info(f"Processing {ccaa} ")
        np_count = len( list( repos.newspaper.find_by( {"ccaa":ccaa} ) ) )
        art_count = len( list( repos.articles.find_by( {"np_ccaa":ccaa, "date":{"$gte": start, "$lt": end}} ) ) )
        
        data.append( {"ccaa":ccaa,"newspaper_count":np_count,"article_count":art_count} )
    return data

def stats_cmd(args:GeneralOptions):
    cmd = CommonCmd(general=args,args=None)
    repos:CrawlerRepos = cmd.connectMongo()
    data = stats_provs(repos, 2024)
    keys = data[0].keys()
    with open('stats_provs_2024.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    data = stats_ccaa(repos, 2024)
    keys = data[0].keys()
    with open('stats_ccaa_2024.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

