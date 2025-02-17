from ...core.backfiller.backfiller import BackFiller
from ...common.consts import ENGINE_ID_WordPress, SUBENGINE_ID_wp_json
from ...common.consts import BfStatus_OK, BfStatus_ERROR
from ...core.model.newspaper import NewsPaper,NewsArticle, NewsPaperBackFill
from ..downloader.wpdownloader import WpReaderContext,WpDownlader, WpArticleReader

import logging

LOG = logging.getLogger(__name__)

class WpBackFiller(BackFiller):
    def __init__(self, repos):
        super().__init__(repos)
        self._engine=ENGINE_ID_WordPress
        self._sub_engine=SUBENGINE_ID_wp_json
        self._downloader=WpDownlader(WpArticleReader(repos))
    
    def do_backFillNews(self,np:NewsPaper,year:int,month:int=None,day:int=None)->NewsPaperBackFill:
        LOG.info(f"BackFilling News of ({np.short_name})\"{np.name}\"")
        if np.n_articulos is None:
            LOG.error("No tiene articulos, no se ha podido obtener informacion previa")
            return None
        
        if np.first_article is None or np.first_month is None:
            LOG.error("Falta informacion previa")
            return None
        
        start,end  = self.get_range(year,month,day)
        ctx = WpReaderContext(news_paper=np)
        LOG.debug(f"  from {start} to {end}")
        
        ret = NewsPaperBackFill(status=BfStatus_OK)

        try:
            tope = 1
            page = 1
            cnt=0
            while page<=tope:
                response = self._downloader.wp_get_dates(ctx,page,start,end)
                if ctx._n_pages > tope:
                    tope=ctx._n_pages
                tmp = ctx.getArticleCount()
                if tmp == cnt:
                    if cnt >0:
                        LOG.error("No se ha encontrado nuevas entradas (¿Protecion?)")
                        ret= NewsPaperBackFill(status=BfStatus_ERROR,msg="No se ha encontrado nuevas entradas (¿Protecion?)")
                    tope = page # paramos
                page+=1
                cnt=tmp
        except Exception as e:
            LOG.error(e)
            return NewsPaperBackFill(status=BfStatus_ERROR,msg=str(e))
        
        LOG.debug(f"found list:({ctx.getArticleCount()}) n_articles:({ctx._n_articles}) n_pages:({ctx._n_pages})")
        articles = ctx.getListArticles()
        self._repos.articles.save_many(articles)
        return ret
        
    


