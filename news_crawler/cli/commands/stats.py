
from news_crawler.cli.commands.common import CommonArgs, CommonCmd, GeneralOptions
from news_crawler.common.dates import get_range
from news_crawler.core.model.repos import CrawlerRepos
from news_crawler.common.consts import provincias, ccaa_geo_map,ccaa_id_geo_map,prov_geo_map
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

def get_prov_n(stats, prov_cod,campo="newspaper_count"):
    import pandas as pd
    if prov_cod not in prov_geo_map:
        print (f"Provincia no encontrada en el mapa: {prov_cod}")
        return None
    prov = prov_geo_map[prov_cod]
    for _, row in stats.iterrows():
        if row['provincia']==prov:
            return row[campo]
        if pd.isna(row['provincia']):
            if row['ccaa'] == prov:
                    return row[campo]
    #print (f"Provincia no encontrada en las stats: {prov_cod} - {prov}")
    return None

def move_canarias(data, cod_ccaa='05'):
    import shapely
    #aumentar canarias latitud en 5 grados
    for idx, row in data.iterrows():
        if row['cod_ccaa']==cod_ccaa:
            geo = row['geometry']
            print(type(geo))
            #es un multipolygon usamos transform
            data.at[idx,'geometry'] = shapely.transform(geo, lambda x=None: x+[9,6.5] )
    return data

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
  
    data = move_canarias(data, cod_ccaa='05' if mode=="ccaa" else '04')
    

  
    if mode=="ccaa":
        data["n_periodicos"] = data.apply(
            lambda row: get_ccaa_n(stats, row['cod_ccaa']), axis=1
        )
        data["n_articulos"] = data.apply(
            lambda row: get_ccaa_n(stats, row['cod_ccaa'], campo="article_count"), axis=1
        )
    else:

        data["n_periodicos"] = data.apply(
            lambda row: get_prov_n(stats, row['cod_prov']), axis=1
        )
        data["n_articulos"] = data.apply(
            lambda row: get_prov_n(stats, row['cod_prov'], campo="article_count"), axis=1
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
        figsize=(12, 8),
        cmap='coolwarm'
    )
    plt.title(f"Mapa de Periodicos por {'Comunidades Autonomas' if mode == 'ccaa' else 'Provincias'} año 2024")
    plt.savefig(f"color_map_papers_{mode}.png")
    ax = geoplot.choropleth(
        data,
        hue="n_articulos",
        projection=gcrs.AlbersEqualArea(),
        edgecolor='darkgrey',
        linewidth=.3,
        legend=True,
        figsize=(12, 8),
        cmap='coolwarm'
        
    )
    plt.title(f"Mapa de Articulos por {'Comunidades Autonomas' if mode == 'ccaa' else 'Provincias'} año 2024")
    plt.savefig(f"color_map_articles_{mode}.png")
    pass

# Funciones para imprimir los mapas de provincias y ccaa
# usadas para faciliatar los dicts de provincias y ccaa en consts.py
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

def print_provs(data,stats):

    print(data.columns)
    data = data.sort_values(by=['name'])
    data["order"] = range(len(data))
    print(data[['cod_prov', 'name', 'cod_ccaa']])
    print(stats.head())

    def t(row):
        
        id_ccaa = ccaa_id_geo_map.get( str(row['cod_ccaa']), None)
        if id_ccaa is None:
            return "Desconocida"
        
        prov_id = row['name'].lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n").replace(" ","").replace("-","")
        if id_ccaa == "extremadura":
            print(row)
            print("EXTREMADURA")
            print(prov_id,"?")
            print(provincias[id_ccaa])

        
        if prov_id not in provincias[id_ccaa]:
            return "Desconocida"
        return prov_id
    data["id_provincia"] = data.apply(lambda row: t(row), axis=1)
    data=data.sort_values(by=['cod_prov'])
    print("Provincias disponibles:")


    for idx, row in data.iterrows():
        print(f"'{row['cod_prov']}':'{row['id_provincia']}', # {row['name']}")