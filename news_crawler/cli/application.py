from ..core.newspapers.prensadigital import PrensaDigitalLister
from ..core.newspapers.prensaescrita import PrensaEscritaLister
from ..core.model.newspaper import NewsPaperRepository
from ..core.detector.detector import NewsPaperDetector
from ..bcube.fetcher.prensaiberica.prensaiberica import BCubePrensaIbericaExtractor
from ..bcube.model.prensaiberica import BcubePiMDRepository
from ..core.model.repos import CrawlerRepos
from ..bcube.fetcher.prensaiberica.pi_stats import PiAnalisys
from ..common.tools import connect_mongo, get_server_name_from_url,get_short_name_from_server_name
from ..wordpress.fetcher.wordpress import WordPressInfoExtractor
import time 

import logging

LOG = logging.getLogger(__name__)

client = connect_mongo()

database = client["general_news"]

repos = CrawlerRepos().connect(database)

newsRepo:NewsPaperRepository = repos.newspaper
bCubePiMdRepo:BcubePiMDRepository = repos.bCubePiMd



def get_newspapers():
    app_pd = PrensaDigitalLister(repo=newsRepo)
    list = app_pd.get_newspapers()
    LOG.info (f"found {len(list)} ")
    app_pd.store_newspapers(list)
    
    app_pe = PrensaEscritaLister(repo=newsRepo)
    list = app_pe.get_newspapers()
    LOG.info (f"found {len(list)} ")
    app_pe.store_newspapers(list)

def detect_newspapers():
    app_detectors = NewsPaperDetector(repo=newsRepo)
    app_detectors.detect_all()

def detect_hoy():
    app_detectors = NewsPaperDetector(repo=newsRepo)
    #hoy = app_detectors._repo.find_one_by({"short_name":"hoy"})
    #hoy = app_detectors._repo.find_one_by({"short_name":"elmon"})
    hoy = app_detectors._repo.find_one_by({"short_name":"diariocostadelsol"})
    LOG.info(app_detectors.detect_one(hoy))

def fetch_bcube_prensa_iberica():
    fetcher = BCubePrensaIbericaExtractor(repos=repos)
    hoy = newsRepo.find_one_by({"short_name":"elcorreoweb"})
    #LOG.info(f"Should be checked: {fetcher.should_be_extracted(hoy)}")
    #fetcher._process_one(hoy)
    #fetcher.fill_stats(hoy)
    fetcher.extract_all()

def fetch_wordpress_info():
    fetcher = WordPressInfoExtractor(repos=repos)
    #np = newsRepo.find_one_by({"short_name":"agendaempresa"})
    np = newsRepo.find_one_by({"short_name":"cadistasfinos"})
    #np = newsRepo.find_one_by({"short_name":"eitb"})
    fetcher._process_one(np)
    fetcher.fill_stats(np)
    #LOG.info(np)
    #fetcher.extract_all(try_no_engine=False)


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

    #pd = PrensaDigitalLister(repos.newspaper)
    #urls = pd.listUrls()
    #LOG.info(urls)
    
    #https://prensadigital.com/
    # LOG.info("{")
    # for ca in urls:
    #     LOG.info(f"  '{ca}':{{")
    #     for prov in urls[ca]:
    #         LOG.info(f"    '{prov}':'https://prensadigital.com{urls[ca][prov]}',")
    #     LOG.info("  },")
    # LOG.info("}")

    LOG.info(get_short_name_from_server_name(get_server_name_from_url("https://www.cincodias.elpais.com/")))
    return exit_code

    LOG.info("{")
if __name__ == "__main__":
    start = time.time() 
    main()
    end = time.time() 
    LOG.info("Execution time: ",end - start) 
