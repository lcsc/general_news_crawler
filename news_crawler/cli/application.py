from ..newspapers.prensadigital import PrensaDigitalLister
from ..newspapers.prensaescrita import PrensaEscritaLister
from pymongo import MongoClient
client = MongoClient("mongodb://host.docker.internal:27017",username='root',
                     password='example',)
database = client["general_news"]

def main() -> int:
    exit_code: int = 0

    database["NewsPapers"].delete_many({})

    app_pd = PrensaDigitalLister(database=database)
    list = app_pd.get_newspapers()
    print (f"found {len(list)} ")
    app_pd.store_newspapers(list)
    
    app_pe = PrensaEscritaLister(database=database)
    list = app_pe.get_newspapers()
    print (f"found {len(list)} ")
    app_pe.store_newspapers(list)

    



    return exit_code


if __name__ == "__main__":
    main()