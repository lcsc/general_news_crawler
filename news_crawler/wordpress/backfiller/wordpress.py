from ...core.backfiller.backfiller import BackFiller
from ...common.consts import ENGINE_ID_WordPress, SUBENGINE_ID_wp_json
from ...core.model.newspaper import NewsPaper,NewsArticle

import logging

LOG = logging.getLogger(__name__)

class WpBackFiller(BackFiller):
    def __init__(self, repos):
        super().__init__(repos)
        self._engine=ENGINE_ID_WordPress
        self._sub_engine=SUBENGINE_ID_wp_json
    
    def do_backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None)->bool:
        LOG.info(f"BackFilling News of ({np.name})\"{np.name}\"")
        start,end  = self.get_range(year,month,day)
        LOG.debug(f"  from {start} to {end}")


