from ..newspapers.prensadigital import PrensaDigitalLister
from ..newspapers.prensaescrita import PrensaEscritaLister
from ..model.newspaper import NewsPaperRepository
from ..detector.detector import NewsPaperDetector
from ..fetcher.prensaiberica.prensaiberica import BCubePrensaIbericaExtractor
from ..model.bcube.prensaiberica import BcubePiMDRepository
from ..model.repos import CrawlerRepos
from ..fetcher.prensaiberica.pi_stats import PiAnalisys

from pymongo import MongoClient
client = MongoClient("mongodb://host.docker.internal:27017",username='root',
                     password='example',)
database = client["general_news"]

repos = CrawlerRepos().connect(database)

newsRepo:NewsPaperRepository = repos.newspaper
bCubePiMdRepo:BcubePiMDRepository = repos.bCubePiMd

def get_newspapers():
    app_pd = PrensaDigitalLister(repo=newsRepo)
    list = app_pd.get_newspapers()
    print (f"found {len(list)} ")
    app_pd.store_newspapers(list)
    
    app_pe = PrensaEscritaLister(repo=newsRepo)
    list = app_pe.get_newspapers()
    print (f"found {len(list)} ")
    app_pe.store_newspapers(list)

def detect_newspapers():
    app_detectors = NewsPaperDetector(repo=newsRepo)
    app_detectors.detect_all()

def detect_hoy():
    app_detectors = NewsPaperDetector(repo=newsRepo)
    #hoy = app_detectors._repo.find_one_by({"short_name":"hoy"})
    #hoy = app_detectors._repo.find_one_by({"short_name":"elmon"})
    hoy = app_detectors._repo.find_one_by({"short_name":"diariocostadelsol"})
    print(app_detectors.detect_one(hoy))

def fetch_bcube_prensa_iberica():
    fetcher = BCubePrensaIbericaExtractor(repos=repos)
    hoy = newsRepo.find_one_by({"short_name":"elcorreoweb"})
    fetcher._process_one(hoy)
    #fetcher.extract_all()

def check_bcube():
    pi = PiAnalisys()
    pi.checkPi()


    
def main() -> int:
    exit_code: int = 0

    #database["NewsPapers"].delete_many({})
    #database["bCubeMetaData"].delete_many({})
    #get_newspapers()
    #detect_newspapers()
    #fetect_hoy()
    fetch_bcube_prensa_iberica()
    #check_bcube()


    return exit_code


if __name__ == "__main__":
    main()