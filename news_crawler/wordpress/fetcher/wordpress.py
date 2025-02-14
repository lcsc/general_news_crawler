
from ...common.consts import ENGINE_ID_WordPress, SUBENGINE_ID_wp_json

from ...common.dates import isValidDay, find_first_month,build_monthly_histogram

from ...core.model.newspaper import NewsPaper, NewsArticle
from ...core.model.repos import CrawlerRepos

from ...core.fetcher.extractor import NewsPaperExtractor
from ..downloader.wpdownloader import WpReaderContext, WpDownlader, WpArticleReader

from typing import List,Dict

import sys

class WordPressInfoExtractor(NewsPaperExtractor):
    def __init__(self,repos:CrawlerRepos):
        super().__init__(repos)
        self._engine = ENGINE_ID_WordPress
        self._subengine = SUBENGINE_ID_wp_json
        self._reader = WpArticleReader(repos)
        self._downloader = WpDownlader(self._reader )
        
    def find_first_month(self,ctx:WpReaderContext)->str:
        #print("Finding FM")
        first_month = find_first_month(histogram=ctx._histogram)
        page=1
        #print(f" ({page}) {first_month}")
        cnt=ctx.getArticleCount()
        while first_month is None:
            page+=1
            
            response = self._downloader.wp_get_url(ctx,page)
            
            if response.status_code != 200:
                print("   Error getting articles")
                return first_month
            tmp = ctx.getArticleCount()
            if len(ctx._lastArticlesRead)==0:
                print("   No articles read")
                return first_month
            if tmp == cnt:
                print("  WARN no new articles found")

            first_month=find_first_month(ctx._histogram)
            #print(f" ({page}) {first_month}")
            cnt=tmp
            
            
            
        return first_month

    def extract_one(self,np:NewsPaper)-> List[NewsArticle]:
        print(f"Testing {np.short_name}")
        ctx = WpReaderContext(np)
        response = self._downloader.wp_get_url(ctx,1)

        if response.status_code!=200:
            if np.engine is None or np.engine.sub_engine is None:
                print("   The NewsPaper is not WP-Json")
            else:
                print("   Error downloading articles")
            return None
        
        ret = ctx.getListArticles()
        if ret == None or len(ret)==0:
            print("  No Articles Found")
            return None
        print(f"  found {len(ret)} articles in page")


        np.n_articulos=ctx._n_articles
        np.first_month=self.find_first_month(ctx)
        #print (f"  FM={np.first_month}")

        ret = ctx.getListArticles()
        self._np_repos.articles.save_many(ret)        
        sys.stdout.flush() #cada vez que terminemos una web
        return ret
    
    # def should_be_extracted(self,np:NewsPaper)->bool:
    #     print("Asking to be extracted")
    #     return True
    def fill_stats(self, np:NewsPaper):
        print(f"Computing stats of {np.short_name} - {np.ccaa}")
        articles = self._np_repos.articles.find_by({"np_name": np.short_name,"np_ccaa": np.ccaa})
        for arti in articles:
            if np.first_article is None:
                np.first_article = arti.date
            if np.first_article> arti.date:
                np.first_article = arti.date
        
        histo = build_monthly_histogram(articles=articles)
        first_month= find_first_month(histo)
        if first_month is not None and np.first_month> first_month:
            np.first_month=first_month