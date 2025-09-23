from news_crawler.bcube.model.bcube import BcubeCategory
from ...core.model.repos import CrawlerRepos
from ...core.model.newspaper import NewsPaper, NewsArticle

from ...core.fetcher.extractor import NewsPaperExtractor,NewsArticleReaderContext,NewsArticleReader
from typing import List
from ...common.tools import print_exception, np_base_path, save_file
from ...common.dates import isValidDay
from ...common.consts import month_thresold,ENGINE_ID_Vocento,SUBENGINE_ID_vc_v22


from ..downloader.vocento import VocentoArticleReader, VocentoArticleReaderContext, VocentoDownloader

import logging
LOG= logging.getLogger(__name__)


class VocentoInfoExtractor(NewsPaperExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        self._engine = ENGINE_ID_Vocento
        self._subengine = SUBENGINE_ID_vc_v22
        self._reader: VocentoArticleReader = VocentoArticleReader(repos)
        self._downloader = VocentoDownloader(self._reader)

    def _find_category(self,ccaa:str,short_name:str,cat_name:str)->BcubeCategory:
        return self._np_repos.bCubeCategories.find_one_by({"ccaa":ccaa,
                                                           "short_name":short_name,
                                                           "cat_name":cat_name})

    def get_categories(self,np:NewsPaper)->list[BcubeCategory]: # list[VocentoCategory]
        home_page = self._downloader.get_mapa_web(np)
        cats = self._reader.get_categories(home_page)
        ret = []
        for c in cats:
            cat = self._find_category(np.ccaa,np.short_name,c)
            if cat is None:
                cat = BcubeCategory(ccaa=np.ccaa,
                                    provincia=np.provincia,
                                    short_name=np.short_name,
                                    cat_name=c,
                                    cat_url=np.real_url + c[1:] if c.startswith('/') else np.real_url + c,
                                    )
                self._np_repos.bCubeCategories.save(cat)
            else:
                LOG.debug(f"  category {c} already in DB")
            ret.append(cat)
        
        return ret

    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        LOG.info(f"extracting {np.short_name} of {np.provincia}")
        categories = self.get_categories(np)
        # Si no hay categorias, no es de este extractor
        if categories is None:
            return None
        
        