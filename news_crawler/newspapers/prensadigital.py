from .lister import NewsPaperLister, PRENSA_DIGITAL
from ..common.tools import get_url,print_exception, normalize_url
from ..model.newspaper import NewsPaperListerInfo

from typing import List
from bs4 import BeautifulSoup

ccaa_urls={
    'andalucia':'https://prensadigital.com/espana/periodicos-de-andalucia/',
    'aragon':'https://prensadigital.com/espana/periodicos-de-aragon/',
    'canarias': 'https://prensadigital.com/espana/periodicos-de-canarias/',
    'cantabria': 'https://prensadigital.com/espana/periodicos-de-cantabria/',
    'castillamancha': 'https://prensadigital.com/espana/periodicos-de-castilla-la-mancha/',
    'castillaleon': 'https://prensadigital.com/espana/periodicos-de-castilla-y-leon/',
    'catalunya':'https://prensadigital.com/espana/periodicos-catalanes/',
    'madrid':'https://prensadigital.com/espana/periodicos-de-madrid/',
    'navarra':'https://prensadigital.com/espana/periodicos-de-navarra/',
    'valencia':'https://prensadigital.com/espana/periodicos-de-comunidad-valenciana/',
    'extremadura':'https://prensadigital.com/espana/periodicos-de-extremadura/',
    'galicia':'https://prensadigital.com/espana/periodicos-de-galicia/',
    'baleares':'https://prensadigital.com/espana/periodicos-de-baleares/',
    'rioja':'https://prensadigital.com/espana/periodicos-de-la-rioja/',
    'pvasco':'https://prensadigital.com/espana/periodicos-vascos/',
    'asturias':'https://prensadigital.com/espana/periodicos-de-asturias/',
    'murcia':'https://prensadigital.com/espana/periodicos-de-murcia/',
    }


class PrensaDigitalLister(NewsPaperLister):


    def _parse_one(self, ccaa, idx, idx_p, p,tipo)->NewsPaperListerInfo:
        pub =p.select_one("h4 a")
        name= pub.text.strip()
        link=pub['href']
        print(f"   {idx} {idx_p}: {name} {link}")
        return (NewsPaperListerInfo(
                    #id=None,
                    ccaa=ccaa,
                    provincia="",
                    name=name,
                    #short_name=get_short_name_from_server_name(get_server_name_from_url(link)),
                    type=tipo,
                    url=normalize_url(link),
                    #real_url=None,
                    #alt_urls=None,
                    src=PRENSA_DIGITAL))

    def get_newspapers_ccaa(self, ccaa)->List[NewsPaperListerInfo]:
        ret = []
        r = get_url(ccaa_urls[ccaa])

        html = r.content.decode("utf-8")
        #with open(ca+".html", "w") as f:
        #    f.write(html)
        #print(html)

        doc = BeautifulSoup(html, 'lxml')
        pubList = doc.find_all("div",{"id":"publishers-list"})
        print (ccaa)
        for idx,l in enumerate(pubList):
            #with open(ca+"."+str(idx)+".html", "w") as f:
            #    f.write(str(l))
            pubs = l.find_all('div',{'class':"stock-card"})
            tipo = l.parent.find("h2").text
            print(f"  {idx}: {len(pubs)} {tipo}")
            for idx_p,p in enumerate(pubs):
                try:
                    ret.append(self._parse_one(ccaa, idx, idx_p, p, tipo))
                except Exception as e: 
                    print_exception(e)

        #print(t)
        return ret
        