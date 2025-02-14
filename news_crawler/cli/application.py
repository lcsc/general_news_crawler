from ..core.newspapers.prensadigital import PrensaDigitalLister
from ..core.newspapers.prensaescrita import PrensaEscritaLister
from ..core.model.newspaper import NewsPaperRepository
from ..core.detector.detector import NewsPaperDetector
from ..bcube.fetcher.prensaiberica.prensaiberica import BCubePrensaIbericaExtractor
from ..bcube.model.prensaiberica import BcubePiMDRepository
from ..core.model.repos import CrawlerRepos
from ..bcube.fetcher.prensaiberica.pi_stats import PiAnalisys
from ..common.tools import connect_mongo
from ..wordpress.fetcher.wordpress import WordPressInfoExtractor
import time 

client = connect_mongo()

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
    #print(f"Should be checked: {fetcher.should_be_extracted(hoy)}")
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
    #print(np)
    #fetcher.extract_all(try_no_engine=False)


def check_bcube():
    pi = PiAnalisys()
    pi.checkPi()
    
def main() -> int:
    exit_code: int = 0

    #database["NewsPapers"].delete_many({})
    #database["bCubeMetaData"].delete_many({})
    #get_newspapers()
    detect_newspapers()
    #fetect_hoy()
    #fetch_bcube_prensa_iberica()
    #check_bcube()
    #fetch_wordpress_info()

    return exit_code


if __name__ == "__main__":
    start = time.time() 
    main()
    end = time.time() 
    print("Execution time: ",end - start) 