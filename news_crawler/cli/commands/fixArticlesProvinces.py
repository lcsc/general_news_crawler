
from news_crawler.cli.commands.common import CommonCmd
from news_crawler.cli.commands.common import CommonArgs, GeneralOptions

from news_crawler.core.model.repos import CrawlerRepos
from typing import Dict, List, Optional

import logging
LOG: logging.Logger = logging.getLogger(__name__)

class FixArticlesProvs(CommonCmd):
    def __init__(self, general:GeneralOptions, args:CommonArgs):
        super().__init__(general, args)
        self.args = args
    
    def fixArticlesProvs(self):
        repos:CrawlerRepos = self.connectMongo()
        filter = self.buildFilterNewsPaper()
        LOG.info(f"Query to Mongo: {filter}") 
        nps = repos.newspaper.find_by(filter)
        nps = list(nps)
        LOG.info(f"Found {len(nps)} newspapers to fix")
        for np in nps:
            LOG.info(f"Fixing newspaper {np.ccaa} {np.short_name} {np.provincia}")
            if np.n_articulos is None or np.n_articulos < 1:
                LOG.warning(f"Newspaper {np.name} has no articles to download, skipping")
                continue
            res =repos.articles.get_collection().update_many(
                {"np_ccaa": np.ccaa, "np_name": np.short_name, "np_provincia": None },
                {"$set": {"np_provincia": np.provincia}}
            )
            LOG.info(f"Updated {res.modified_count} articles for newspaper {np.ccaa} {np.short_name} {np.provincia}")
        LOG.info("Fixing articles provinces completed.")