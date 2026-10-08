

from news_crawler.core.cienallm import CienaConnector

class CienaCommand():
    def __init__(self):
        self.ciena = CienaConnector()
    
    def ls(self):
        baseConfigs = self.ciena.ls_base()
        print("Base configurations:")
        for key,value in baseConfigs.items():
            print(f"{key}: {value}")

        