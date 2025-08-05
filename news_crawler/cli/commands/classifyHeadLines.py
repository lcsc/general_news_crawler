
from news_crawler.cli.commands.common import CommonCmd
from news_crawler.cli.commands.common import CommonArgs, GeneralOptions

from news_crawler.core.model.repos import CrawlerRepos
from typing import Dict, List, Optional
from news_crawler.core.classifier import DroughtPickyKeywordClassifier

import logging
LOG: logging.Logger = logging.getLogger(__name__)

class ClassifyHeadLines(CommonCmd):
    def __init__(self, general:GeneralOptions, args:CommonArgs):
        super().__init__(general, args)
        self.args = args

    def classifyHeadLines(self):
        repos:CrawlerRepos = self.connectMongo()
        classifier = DroughtPickyKeywordClassifier()
        
        filter = self.buildFilterNewsPaper()
        LOG.info(f"Query to Mongo: {filter}") 
        nps = repos.newspaper.find_by(filter)
        nps = list(nps)
        LOG.info(f"Found {len(nps)} newspapers to classify headlines")
        
        for np in nps:
            LOG.info(f"Classifying headlines for newspaper {np.ccaa} {np.short_name} {np.provincia}")
            if np.n_articulos is None or np.n_articulos < 1:
                LOG.warning(f"Newspaper {np.name} has no articles to classify, skipping")
                continue
            articles = list(repos.articles.find_by(
                {"np_ccaa": np.ccaa, "np_name": np.short_name, "np_provincia": np.provincia, "is_headline_drought": None}
            ))
            count = 0
            for article in articles:
                article.is_headline_drought = classifier.classify(article.article_headline)
                repos.articles.save(article)
                count += 1
                if count % 1000 == 0:
                    LOG.info(f"Processed {count} articles for newspaper {np.ccaa} {np.short_name} {np.provincia}")
            LOG.info(f"Classified {count} articles for newspaper {np.ccaa} {np.short_name} {np.provincia}")

        LOG.info("Classifying headlines completed.")