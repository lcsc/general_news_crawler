from ..core.newspapers.prensadigital import PrensaDigitalLister
from ..core.newspapers.prensaescrita import PrensaEscritaLister
from ..core.model.newspaper import NewsPaperRepository, NewsPaper
from ..core.detector.detector import NewsPaperDetector
from ..bcube.fetcher.prensaiberica.prensaiberica import BCubePrensaIbericaExtractor
from ..bcube.model.prensaiberica import BcubePiMDRepository
from ..core.model.repos import CrawlerRepos
from ..bcube.fetcher.prensaiberica.pi_stats import PiAnalisys
from ..common.tools import connect_mongo, get_server_name_from_url,get_short_name_from_server_name
from ..wordpress.fetcher.wordpress import WordPressInfoExtractor
from ..core.newspapers.lister import getIdBasic
from ..common import consts

import json
import time 

import logging

from typing import List
from ..bcube.model.bcube import BcubeCategory

LOG = logging.getLogger(__name__)
client = connect_mongo()
database = client["general_news"]
repos = CrawlerRepos().connect(database)

newsRepo:NewsPaperRepository = repos.newspaper
bCubePiMdRepo:BcubePiMDRepository = repos.bCubePiMd

'''
Funciones para ejecutar los diferentes procesos de la aplicación y que no estan en el CLI
'''

def check_bcube():
    pi = PiAnalisys()
    pi.checkPi()

def getProvName(prov:str):
    prov=prov.lower()
    prov=prov.replace("á","a")
    prov=prov.replace("é","e")
    prov=prov.replace("í","i")
    prov=prov.replace("ó","o")
    prov=prov.replace("ú","u")

    if "/" in prov:
        prov =prov.split("/")[1].removeprefix(" ")
    if " - " in prov:
        prov =prov.split("-")[0].removesuffix(" ")
    prov = prov.replace(" ","")
    return prov

def build_provs():
    nps = repos.newspaper.find_by({})

    ccaas = {}
    for np in nps:
        ca = np.ccaa
        prov = np.provincia
        if ca not in ccaas:
            ccaas[ca]=[]
        if prov is not None and prov not in ccaas[ca]:
            ccaas[ca].append(prov)
    

    #LOG.info(ccaas)
    
    # for ca in ccaas:
    #     for p in ccaas[ca]:
    #         LOG.info(f"'{p}':'{getProvName(p)}'")
    
    # return
    
    LOG.info ("{")
    for ca in ccaas:
        provs= ccaas[ca]
        if len(provs)==0:
            LOG.info(f"  '{ca}':['{ca}'],")    
        elif len(provs)==1:
            LOG.info(f"  '{ca}':['{provs[0]}'],")    
        else:
            LOG.info(f"  '{ca}':[")
            for p in provs:
                LOG.info(f"    '{p}',")
            LOG.info("  ],")
    LOG.info ("}")

def build_pd_ursl():
    pd = PrensaDigitalLister(repos.newspaper)
    urls = pd.listUrls()
    LOG.info(urls)
    
    #https://prensadigital.com/
    LOG.info("{")
    for ca in urls:
        LOG.info(f"  '{ca}':{{")
        for prov in urls[ca]:
            LOG.info(f"    '{prov}':'https://prensadigital.com{urls[ca][prov]}',")
        LOG.info("  },")
    LOG.info("}")

def print_backfill_stats(ccaa:str=None,short_name:str=None):
    np:NewsPaper = repos.newspaper.find_one_by({"ccaa":ccaa,"short_name":short_name})
    if np.backfill is not None:
        LOG.info(np.backfill["2024"]["12"])
    cats:List[BcubeCategory] = repos.bCubeCategories.find_by({"ccaa":ccaa,"short_name":short_name})
    for cat in cats:
        if cat.backfill is not None:
            if cat.backfill['2024']['12'].status != "OK":
                LOG.info(f"   {cat.cat_name} -> {cat.backfill['2024']['12']}")
        else :
            LOG.info(f"   {cat.cat_name} -> None")

def getCaID(name:str)->str:
    ca = getIdBasic(name)

    if ca in consts.ccaa:
        return ca
    nobasic={
        "castilla-lamancha":"castillamancha",
        "castilla-leon":"castillaleon",
        "cataluña":"catalunya",
        "ceuta":"ceutamelilla",
        "paisvasco":"pvasco",
        "melilla":"ceutamelilla",
        "comunidadvalenciana":"valencia",
        "larioja":"rioja",
    }
    if ca in nobasic:
        return nobasic[ca]
    else:
        LOG.error(f"Unknown ccaa: {name} - {ca}")
    return ca

def getProvId(ca:str, name:str):
    prov = getProvName(name)

    if prov in consts.provincias[ca]:
        return prov
    

    for c in consts.provincias:
        #puede que esta mal la ca
        if prov in consts.provincias[c]:
            #LOG.warning(f"     {name} encontrada en {c} en vez de {ca}")
            return prov
    nobasic={ "acoruña":"lacoruña",
             "larioja":"rioja",
             "illesbalears":"baleares",
             "ourense":"orense",
             "santacruzdetenerife":"santacruz",}
    
    ret=None

    if prov in nobasic:
        ret = nobasic[prov]
    
    for c in consts.provincias:
        if ret in consts.provincias[c]:
            return ret

    LOG.error(f"Unknown provincia: {name} - {prov} - {ret} ({ca})")
    return None

def extract_ccas():
    comunities= json.load(open("dashboard/src/assets/communities.geojson"))

    ccass={}

    for f in comunities["features"]:
        name = f["properties"]["name"]
        code = f["properties"]["cod_ccaa"]
        #LOG.info(f"  '{code}':'{name}',")
        ccass[code]={"name":name, "id":getCaID(name)}
    
    LOG.info(ccass)

    provinces = json.load(open("dashboard/src/assets/provinces.geojson"))
    provs = {}
    for f in provinces["features"]:
        name = f["properties"]["name"]
        code = f["properties"]["cod_prov"]
        cod_ccaa = f["properties"]["cod_ccaa"]
        #LOG.info(f"  '{code}':'{name}',")
        provs[code]={"name":name, "id":getProvId(ccass[cod_ccaa]["id"], name)}
    LOG.info(provs)

def main() -> int:
    exit_code: int = 0

    #database["NewsPapers"].delete_many({})
    #database["bCubeMetaData"].delete_many({})
    #get_newspapers()
    #detect_newspapers()
    #fetect_hoy()
    #fetch_bcube_prensa_iberica()
    #check_bcube()
    #fetch_wordpress_info()
    #build_provs()
    #build_pd_ursl
    #LOG.info(get_short_name_from_server_name(get_server_name_from_url("https://www.cincodias.elpais.com/")))
    print_backfill_stats("andalucia","diariocordoba")
    #extract_ccas()
    
    return exit_code

if __name__ == "__main__":
    start = time.time() 
    main()
    end = time.time() 
    LOG.info("Execution time: ",end - start) 
