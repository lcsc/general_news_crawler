
from news_crawler.cli.commands.common import CommonArgs, CommonCmd, GeneralOptions
from news_crawler.common.dates import get_range
from news_crawler.core.model.repos import CrawlerRepos
from news_crawler.common.consts import provincias, ccaa_geo_map
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

def get_ccaa_n(stats, ccaa_cod,campo="newspaper_count"):
    if ccaa_cod not in ccaa_geo_map:
        return None
    ccaa = ccaa_geo_map[ccaa_cod]

    for _, row in stats.iterrows():
        if row['ccaa']==ccaa:
            return row[campo]
    return None

def color_map_cmd(mode, csv_file, geo_file):
    import geopandas as gpd
    import geoplot
    import geoplot.crs as gcrs
    import matplotlib.pyplot as plt
    import pandas as pd
    data = gpd.read_file(
        geo_file
    )

    stats = pd.read_csv(csv_file)
    
    #print(data.columns)
    #print(data[['cod_ccaa', 'noml_ccaa', 'name', 'cartodb_id']].head())
    #print(stats.head())

    if mode=="ccaa":
        data["n_periodicos"] = data.apply(
            lambda row: get_ccaa_n(stats, row['cod_ccaa']), axis=1
        )
        data["n_articulos"] = data.apply(
            lambda row: get_ccaa_n(stats, row['cod_ccaa'], campo="article_count"), axis=1
        )
    #print(data[['cod_ccaa', 'name', 'n_periodicos', 'n_articulos']].head())

    #plt.figure(figsize=(12, 8))
    ax = geoplot.choropleth(
        data,
        hue="n_periodicos",
        projection=gcrs.AlbersEqualArea(),
        edgecolor='darkgrey',
        linewidth=.3,
        legend=True,
        figsize=(12, 8)
    )
    plt.title(f"Mapa de Periodicos por {mode}")
    plt.savefig(f"color_map_papers_{mode}.png")
    ax = geoplot.choropleth(
        data,
        hue="n_articulos",
        projection=gcrs.AlbersEqualArea(),
        edgecolor='darkgrey',
        linewidth=.3,
        legend=True,
        figsize=(12, 8)
    )
    plt.title(f"Mapa de Articulos por {mode} año 2024")
    plt.savefig(f"color_map_articles_{mode}.png")
    pass

def print_ccaa(data):
    ccaa = sorted(provincias.keys())
    # Dataframe con las columanas cod_ccaa y noml_ccaa de data
    ccaas = data[['cod_ccaa','noml_ccaa']].copy()

    def t(row):
        id_ccaa = int(row['cod_ccaa']) -1
        if id_ccaa <0 or id_ccaa >= len(ccaa):
            return "Desconocida"
        return ccaa[id_ccaa]

    ccaas["id_ccaa"] = ccaas.apply(lambda row: t(row), axis=1)
    ccaas=ccaas.sort_values(by=['cod_ccaa'])
    print("CCAA disponibles:")
    for idx, row in ccaas.iterrows():
        print(f"'{row['cod_ccaa']}':'{row['id_ccaa']}', # {row['noml_ccaa']}")