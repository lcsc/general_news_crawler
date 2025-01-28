from ..newspapers.prensadigital import PrensaDigitalLister
from ..newspapers.prensaescrita import PrensaEscritaLister
from ..model.newspaper import NewsPaperRepository

from ..detector.detector import NewsPaperDetector
from pymongo import MongoClient
client = MongoClient("mongodb://host.docker.internal:27017",username='root',
                     password='example',)
database = client["general_news"]
newsRepo = NewsPaperRepository(database=database)

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

def main() -> int:
    exit_code: int = 0

    #database["NewsPapers"].delete_many({})
    #get_newspapers()
    detect_newspapers()
    #detect_hoy()
    



    return exit_code


if __name__ == "__main__":
    main()